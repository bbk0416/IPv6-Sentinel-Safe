"""Dependency-light release matrix checks for reviewer handoff consistency.

The safe release ID is ``27.0.0-safe``. The Python package metadata uses the
normalized PEP 440 package version ``27.0.0`` because hyphenated local release
labels are not valid project versions in ``pyproject.toml``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

CURRENT_VERSION = "27.0.0-safe"
CURRENT_PYPROJECT_VERSION = "27.0.0"

REQUIRED_VERSION_MARKERS = {
    "settings.py": CURRENT_VERSION,
    "pyproject.toml": f'version = "{CURRENT_PYPROJECT_VERSION}"',
    "project_manifest.json": f'"version": "{CURRENT_VERSION}"',
    "docs/api/openapi.yaml": f"version: {CURRENT_VERSION}",
    "README.md": CURRENT_VERSION,
    "VALIDATION_REPORT.md": CURRENT_VERSION,
    "PROJECT_COMPLETION_REPORT.md": CURRENT_VERSION,
    "RELEASE_NOTES_v27.md": CURRENT_VERSION,
}


def check_release_matrix(root: Path | str = ".") -> Dict[str, object]:
    root_path = Path(root)
    checks: List[Dict[str, object]] = []

    for rel_path, marker in REQUIRED_VERSION_MARKERS.items():
        path = root_path / rel_path
        if not path.exists():
            checks.append({"name": rel_path, "ok": False, "detail": "missing file"})
            continue
        text = path.read_text(encoding="utf-8")
        checks.append({"name": rel_path, "ok": marker in text, "detail": f"expected marker: {marker}"})

    stale_current_notes = []
    for note in sorted(root_path.glob("RELEASE_NOTES_v*.md")):
        if note.name == "RELEASE_NOTES_v27.md":
            continue
        try:
            text = note.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if CURRENT_VERSION in first_line:
            stale_current_notes.append(note.name)

    checks.append({
        "name": "older_release_notes_do_not_claim_current_version",
        "ok": not stale_current_notes,
        "detail": stale_current_notes or "none",
    })

    status = "pass" if all(c["ok"] for c in checks) else "fail"
    return {
        "status": status,
        "version": CURRENT_VERSION,
        "package_version": CURRENT_PYPROJECT_VERSION,
        "check_count": len(checks),
        "checks": checks,
        "notes": [
            "pyproject.toml intentionally uses the normalized PEP 440 package version.",
            "Reviewer-facing docs and APIs use the safe release ID.",
        ],
    }
