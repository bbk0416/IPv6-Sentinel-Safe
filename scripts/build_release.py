from __future__ import annotations

import argparse
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.clean_release_artifacts import clean  # noqa: E402
EXCLUDED_PARTS = {'.venv', 'venv', 'env', '.testvenv', 'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'logs', 'data', 'backup'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo', '.log', '.db', '.sqlite', '.zip'}


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return not any(part in EXCLUDED_PARTS for part in rel.parts) and path.suffix.lower() not in EXCLUDED_SUFFIXES


def _release_sort_key(path: Path) -> str:
    """Return a platform-stable ZIP member order key."""
    return path.relative_to(ROOT).as_posix()


def _iter_included_files() -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(name for name in dirnames if name not in EXCLUDED_PARTS)
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            if include(path):
                files.append(path)
    return sorted(files, key=_release_sort_key)


def build(output: Path, *, clean_first: bool = False) -> None:
    if clean_first:
        clean(ROOT)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in _iter_included_files():
            if path.resolve() != output.resolve():
                zf.write(path, ROOT.name / path.relative_to(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description='Build a sanitized IPv6 Sentinel Safe release ZIP.')
    parser.add_argument('--output', default=str(ROOT.parent / f'{ROOT.name}.zip'))
    parser.add_argument('--no-clean', action='store_true', help='Skip cleaning generated caches before packaging.')
    args = parser.parse_args()
    build(Path(args.output), clean_first=not args.no_clean)
    print(f'[OK] release package written: {args.output}')


if __name__ == '__main__':
    main()
