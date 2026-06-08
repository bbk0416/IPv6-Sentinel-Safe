#!/usr/bin/env python3
"""Validate a built release ZIP without extracting it."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.clean_release_artifacts import clean  # noqa: E402
from scripts.build_release import build  # noqa: E402
from settings import APP_VERSION  # noqa: E402

BLOCKED_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv", "env", ".testvenv", "node_modules", "logs", "data", "backup"}
BLOCKED_SUFFIXES = {".pyc", ".pyo", ".log", ".db", ".sqlite", ".zip"}
REQUIRED_FILES = {
    "README.md",
    "requirements.txt",
    "app.py",
    "settings.py",
    "project_manifest.json",
    "docs/api/openapi.yaml",
    "docs/quality/RELEASE_ZIP.md",
    "scripts/check_release_zip.py",
    "scripts/clean_release_artifacts.py",
    "scripts/check_file_inventory.py",
    "docs/quality/FILE_INVENTORY.md",
    "docs/release/FILE_INVENTORY.json",
    "RELEASE_NOTES_v27.md",
    "docs/quality/FINAL_HANDOFF.md",
    "docs/quality/ROUTE_HYGIENE.md",
    "scripts/final_handoff_check.py",
    "scripts/check_route_hygiene.py",
    "docs/quality/VALIDATION_HYGIENE.md",
    "scripts/check_validation_hygiene.py",
    "scripts/run_clean_validation.py",
    "docs/quality/CAPABILITY_BOUNDARY.md",
    "scripts/check_capability_boundary.py",
}


def _member_payload(names: list[str]) -> tuple[str | None, set[str]]:
    top_levels = {name.split("/", 1)[0] for name in names if name and not name.endswith("/")}
    root_name = next(iter(top_levels)) if len(top_levels) == 1 else None
    files = set()
    if root_name:
        prefix = root_name + "/"
        files = {name.removeprefix(prefix) for name in names if name.startswith(prefix) and not name.endswith("/")}
    return root_name, files


def inspect_zip(path: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return {"status": "fail", "errors": [f"zip not found: {path}"], "warnings": [], "file_count": 0}
    with zipfile.ZipFile(path) as zf:
        bad = zf.testzip()
        if bad:
            errors.append(f"corrupt zip member: {bad}")
        names = zf.namelist()
    root_name, files = _member_payload(names)
    if not root_name:
        errors.append("zip should contain exactly one top-level project directory")
    missing = sorted(REQUIRED_FILES - files)
    if missing:
        errors.append("missing required file(s): " + ", ".join(missing))
    blocked = []
    for name in names:
        parts = Path(name).parts
        if any(part in BLOCKED_PARTS for part in parts) or Path(name).suffix.lower() in BLOCKED_SUFFIXES:
            blocked.append(name)
    if blocked:
        errors.append("blocked artifact(s) in zip: " + ", ".join(blocked[:30]))
    if f"{root_name}/project_manifest.json" in names:
        with zipfile.ZipFile(path) as zf:
            manifest = json.loads(zf.read(f"{root_name}/project_manifest.json").decode("utf-8"))
        if manifest.get("version") != APP_VERSION:
            errors.append(f"manifest version {manifest.get('version')} != {APP_VERSION}")
        if not manifest.get("safe_mode") or not manifest.get("simulation_mode"):
            errors.append("manifest must declare safe simulation mode")
    return {
        "status": "pass" if not errors else "fail",
        "version": APP_VERSION,
        "zip": str(path),
        "root": root_name,
        "file_count": len(files),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and/or validate a sanitized release ZIP.")
    parser.add_argument("zip_path", nargs="?", help="Existing ZIP to inspect. If omitted, a temporary ZIP is built.")
    parser.add_argument("--no-clean", action="store_true", help="Do not clean generated artifacts before building a temporary ZIP.")
    args = parser.parse_args()

    if args.zip_path:
        payload = inspect_zip(Path(args.zip_path))
    else:
        if not args.no_clean:
            clean(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "release.zip"
            build(candidate)
            payload = inspect_zip(candidate)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
