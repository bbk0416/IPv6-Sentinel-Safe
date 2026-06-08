"""Release identity consistency checks.

The project has many reviewer-facing files. This module makes sure the safe
release identity is updated in code, manifest, OpenAPI, README handoff sections,
and validation documents, while pyproject.toml uses the normalized PEP 440
package version. It is static and read-only.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CURRENT_VERSION = "27.0.0-safe"
CURRENT_PYPROJECT_VERSION = "27.0.0"
CURRENT_RELEASE_NOTE = "RELEASE_NOTES_v27.md"


@dataclass(frozen=True)
class ReleaseIdentityCheck:
    name: str
    ok: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def _json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _pyproject_version(pyproject_text: str) -> str | None:
    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', pyproject_text, re.MULTILINE)
    return match.group(1) if match else None


def run_release_identity_check(*, app_root: Path, app_version: str) -> dict[str, Any]:
    manifest = _json(app_root / "project_manifest.json")
    pyproject = _read(app_root / "pyproject.toml")
    openapi = _read(app_root / "docs" / "api" / "openapi.yaml")
    readme = _read(app_root / "README.md")
    validation_report = _read(app_root / "VALIDATION_REPORT.md")
    completion_report = _read(app_root / "PROJECT_COMPLETION_REPORT.md")
    release_manifest = _read(app_root / "docs" / "release" / "RELEASE_PACKAGE_MANIFEST.md")
    release_notes = manifest.get("release_notes", []) if isinstance(manifest.get("release_notes"), list) else []

    docs_blob = "\n".join([readme, validation_report, completion_report, release_manifest])
    checks = [
        ReleaseIdentityCheck(
            "settings_version_matches_current_release",
            app_version == CURRENT_VERSION,
            f"settings/app version={app_version}; expected={CURRENT_VERSION}",
        ),
        ReleaseIdentityCheck(
            "pyproject_version_matches_normalized_package_version",
            _pyproject_version(pyproject) == CURRENT_PYPROJECT_VERSION,
            f"pyproject package version={_pyproject_version(pyproject)}; expected normalized PEP 440 version={CURRENT_PYPROJECT_VERSION}",
        ),
        ReleaseIdentityCheck(
            "manifest_version_matches_current_release",
            manifest.get("version") == CURRENT_VERSION,
            f"manifest version={manifest.get('version')}; expected={CURRENT_VERSION}",
        ),
        ReleaseIdentityCheck(
            "openapi_version_matches_current_release",
            f"version: {CURRENT_VERSION}" in openapi,
            "OpenAPI info.version must match the safe release version.",
        ),
        ReleaseIdentityCheck(
            "current_release_note_is_declared_once",
            release_notes.count(CURRENT_RELEASE_NOTE) == 1,
            f"{CURRENT_RELEASE_NOTE} count in manifest.release_notes={release_notes.count(CURRENT_RELEASE_NOTE)}",
        ),
        ReleaseIdentityCheck(
            "manifest_release_notes_are_unique",
            len(release_notes) == len(set(release_notes)),
            "manifest.release_notes should not contain duplicate entries.",
        ),
        ReleaseIdentityCheck(
            "current_release_docs_are_visible",
            all(token in docs_blob for token in (CURRENT_VERSION, "v27")),
            "README, validation, completion, and release manifest should expose the current release identity.",
        ),
    ]
    failures = [check for check in checks if not check.ok]
    return {
        "status": "pass" if not failures else "fail",
        "version": CURRENT_VERSION,
        "checks": [check.to_dict() for check in checks],
        "summary": {"total": len(checks), "passed": len(checks) - len(failures), "failures": len(failures)},
    }
