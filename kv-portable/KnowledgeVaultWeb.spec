# -*- mode: python ; coding: utf-8 -*-
# 경량 웹 exe (Whisper 미포함). build_web_exe.bat 가 kv/profiles/kv-web 를 먼저 복사함.

a = Analysis(
    ['kvweb_launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('kv-web', 'kv-web'),
        ('profiles', 'profiles'),
        ('config.portable.yaml', '.'),
    ],
    hiddenimports=[
        'kv', 'kv.config', 'kv.webserver', 'kv.ask', 'kv.llm', 'kv.search',
        'kv.ingest', 'kv.refine', 'kv.tags', 'kv.import_refs', 'kv.webfetch',
        'kv.converters', 'kv.converters.excel_conv', 'kv.converters.pdf',
        'kv.converters.pptx_conv', 'kv.converters.hwp', 'kv.converters.html_conv',
        'kv.converters.image', 'kv.converters.notes', 'kv.converters.markitdown_conv',
        'yaml', 'openpyxl', 'pypdf', 'pptx', 'docx', 'olefile',
        'PIL', 'PIL.Image', 'pytesseract',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # 무거운 ML/오디오 스택 제외 → 경량
    excludes=[
        'faster_whisper', 'whisper', 'torch', 'ctranslate2', 'onnxruntime',
        'transformers', 'tensorflow', 'scipy', 'pandas', 'matplotlib', 'tkinter',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='KnowledgeVaultWeb',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
