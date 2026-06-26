from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from kv.config import VAULT_REFINED, index_db_path
from kv.import_refs import doc_from_reference, iter_reference_files
from kv.tags import parse_markdown


@dataclass
class SearchHit:
    path: str
    title: str
    score: float
    snippet: str
    tags: list[str]
    keywords: list[str]


def _connect() -> sqlite3.Connection:
    db = index_db_path()
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


def rebuild_index() -> int:
    """정제 MD + 볼트 참조 문서 FTS 인덱스."""
    conn = _connect()
    conn.execute("DROP TABLE IF EXISTS docs_fts")
    conn.execute("DROP TABLE IF EXISTS docs")
    conn.execute("""
        CREATE TABLE docs (
            id INTEGER PRIMARY KEY,
            path TEXT UNIQUE,
            title TEXT,
            body TEXT,
            tags TEXT,
            keywords TEXT,
            source_type TEXT
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE docs_fts USING fts5(
            title, body, tags, keywords,
            content='docs', content_rowid='id'
        )
    """)

    count = 0

    def _insert(doc: dict) -> None:
        nonlocal count
        conn.execute(
            "INSERT OR REPLACE INTO docs (path, title, body, tags, keywords, source_type) VALUES (?,?,?,?,?,?)",
            (doc["path"], doc["title"], doc["body"], doc["tags"], doc["keywords"], doc["source_type"]),
        )
        count += 1

    for path in sorted(VAULT_REFINED.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, body = parse_markdown(text)
        _insert({
            "path": str(path),
            "title": fm.get("title", path.stem),
            "body": body,
            "tags": ",".join(fm.get("tags", [])),
            "keywords": ",".join(fm.get("keywords", [])),
            "source_type": fm.get("source_type", "collected"),
        })

    for path, source_type, extra_tags in iter_reference_files():
        _insert(doc_from_reference(path, source_type, extra_tags))

    conn.execute("INSERT INTO docs_fts(docs_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()
    return count


def search(
    query: str,
    *,
    tag: str | None = None,
    source_type: str | None = None,
    limit: int = 20,
) -> list[SearchHit]:
    conn = _connect()
    try:
        conn.execute("SELECT 1 FROM docs_fts LIMIT 1")
    except sqlite3.OperationalError:
        rebuild_index()

    sql = """
        SELECT d.path, d.title, d.tags, d.keywords,
               snippet(docs_fts, 1, '**', '**', '...', 40) AS snip,
               bm25(docs_fts) AS score
        FROM docs_fts
        JOIN docs d ON docs_fts.rowid = d.id
        WHERE docs_fts MATCH ?
    """
    params: list = [query]

    if tag:
        sql += " AND d.tags LIKE ?"
        params.append(f"%{tag}%")
    if source_type:
        sql += " AND d.source_type = ?"
        params.append(source_type)

    sql += " ORDER BY score LIMIT ?"
    params.append(limit)

    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        rebuild_index()
        rows = conn.execute(sql, params).fetchall()

    hits: list[SearchHit] = []
    for r in rows:
        hits.append(SearchHit(
            path=r["path"],
            title=r["title"],
            score=r["score"],
            snippet=r["snip"] or "",
            tags=(r["tags"] or "").split(",") if r["tags"] else [],
            keywords=(r["keywords"] or "").split(",") if r["keywords"] else [],
        ))
    conn.close()
    return hits
