#!/usr/bin/env python3
"""Parse repository Python sources and, when available, YAML files."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    python_files = sorted((ROOT / "scripts").rglob("*.py"))
    for path in python_files:
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    print(f"Python syntax OK: {len(python_files)} files")

    try:
        import yaml
    except ModuleNotFoundError:
        print("YAML parse skipped: PyYAML is not installed in this lightweight environment")
        return

    yaml_files = sorted(ROOT.rglob("*.yml")) + sorted(ROOT.rglob("*.yaml"))
    for path in yaml_files:
        yaml.safe_load(path.read_text(encoding="utf-8"))
    print(f"YAML parse OK: {len(yaml_files)} files")


if __name__ == "__main__":
    main()
