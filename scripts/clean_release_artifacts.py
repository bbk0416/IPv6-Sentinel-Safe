#!/usr/bin/env python3
"""Remove generated artifacts before building or sharing a release ZIP.

This script is intentionally conservative. It removes Python caches, test caches,
simulator runtime folders, and stray nested ZIP files that are reproducible and should not be committed or
included in reviewer handoff archives.
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
RUNTIME_DIRS = {"logs", "data"}
FILE_SUFFIXES = {".pyc", ".pyo", ".log", ".zip"}
WORKSPACE_SKIP_DIRS = {".venv", "venv", "env", ".testvenv", ".git", "node_modules"}


def collect_targets(root: Path) -> list[Path]:
    targets: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        kept_dirs = []
        for dirname in dirnames:
            child = current / dirname
            if dirname in WORKSPACE_SKIP_DIRS:
                continue
            if dirname in DIR_NAMES or dirname in RUNTIME_DIRS:
                targets.append(child)
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for filename in filenames:
            path = current / filename
            if path.suffix.lower() in FILE_SUFFIXES:
                targets.append(path)
    # Delete deepest paths first so nested files do not conflict with parent dir removal.
    return sorted(set(targets), key=lambda item: len(item.parts), reverse=True)


def clean(root: Path, *, dry_run: bool = False) -> list[str]:
    removed: list[str] = []
    for target in collect_targets(root):
        if not target.exists():
            continue
        removed.append(str(target.relative_to(root)))
        if dry_run:
            continue
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean generated release artifacts from the source tree.")
    parser.add_argument("--dry-run", action="store_true", help="List what would be removed without deleting anything.")
    args = parser.parse_args()
    removed = clean(ROOT, dry_run=args.dry_run)
    verb = "would remove" if args.dry_run else "removed"
    print(f"[OK] {verb} {len(removed)} generated artifact(s)")
    for item in removed[:50]:
        print(f" - {item}")
    if len(removed) > 50:
        print(f" - ... {len(removed) - 50} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
