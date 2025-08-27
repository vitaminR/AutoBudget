#!/usr/bin/env python3
"""
Embed Index (lightweight)

Builds a simple file manifest for retrieval-style search without external deps.

Usage:
  python scripts/embed_index.py rebuild
  python scripts/embed_index.py search "query"

Behavior:
- rebuild(): scans repo for { .md, .py, .ts, .tsx, .json, .yaml, .yml }
  while skipping dirs: node_modules, dist, build, .git, .gemini, secrets
  and writes data/faiss_index/meta.json with a list of files (relative paths).
- search(q): loads meta.json and prints up to 10 hits whose basenames contain q.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Iterable, List

ROOT = Path.cwd()
OUT_DIR = ROOT / "data" / "faiss_index"
META = OUT_DIR / "meta.json"

ALLOWED_EXTS = {".md", ".py", ".ts", ".tsx", ".json", ".yaml", ".yml"}
SKIP_DIRS = {"node_modules", "dist", "build", ".git", ".gemini", "secrets"}


def _iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        # prune
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() in ALLOWED_EXTS:
                yield p


def rebuild() -> List[str]:
    files = sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in _iter_files(ROOT))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "root": str(ROOT),
        "generated": datetime.utcnow().isoformat() + "Z",
        "count": len(files),
        "files": files,
    }
    META.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {META} with {len(files)} files")
    return files


def search(query: str) -> List[str]:
    if not META.exists():
        print("Index missing; run 'rebuild' first.")
        return []
    data = json.loads(META.read_text(encoding="utf-8"))
    files = data.get("files", [])
    q = (query or "").lower()
    hits = [f for f in files if q in Path(f).name.lower()]
    for i, f in enumerate(hits[:10], 1):
        print(f"{i}. {f}")
    return hits[:10]


def _main(argv: List[str]) -> int:
    if not argv:
        print(__doc__.strip())
        return 0
    cmd = argv[0]
    if cmd == "rebuild":
        rebuild()
        return 0
    if cmd == "search":
        if len(argv) < 2:
            print("Usage: search \"query\"")
            return 2
        search(" ".join(argv[1:]))
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
