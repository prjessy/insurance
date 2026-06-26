from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConvertResult:
    title: str
    body: str
    source_type: str
    extra_meta: dict | None = None


class BaseConverter(ABC):
    source_type: str
    extensions: set[str]

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    @abstractmethod
    def convert(self, path: Path) -> ConvertResult:
        ...
