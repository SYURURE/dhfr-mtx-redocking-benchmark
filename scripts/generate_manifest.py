#!/usr/bin/env python3
"""Regenerate MANIFEST.sha256 for every versioned package file."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"
EXCLUDED_DIRECTORY_NAMES = {".git", "__pycache__"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    files = sorted(
        (
            path
            for path in ROOT.rglob("*")
            if path.is_file()
            and path.resolve() != MANIFEST.resolve()
            and not any(part in EXCLUDED_DIRECTORY_NAMES for part in path.parts)
        ),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )
    lines = [
        f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}"
        for path in files
    ]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {MANIFEST.name}: {len(files)} files")


if __name__ == "__main__":
    main()
