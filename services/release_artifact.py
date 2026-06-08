"""Release artifact hygiene checks.

The project is distributed as a source ZIP for portfolio review. This module
checks that the tree looks like a clean release package: no runtime cache/data,
required handoff files are present, current release notes are included, and the
package still declares its simulation-only boundary. It is static and read-only.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CURRENT_VERSION = "27.0.0-safe"
CURRENT_RELEASE_NOTE = "RELEASE_NOTES_v27.md"

WORKSPACE_LOCAL_PATH_PARTS = {".git", ".venv", "venv", "env", ".testvenv"}
BLOCKED_PATH_PARTS = {"backup"}
GENERATED_RUNTIME_PATH_PARTS = {"data", "logs"}
CACHE_PATH_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}

BLOCKED_SUFFIXES = {".sqlite", ".db", ".zip"}
GENERATED_RUNTIME_SUFFIXES = {".log"}
CACHE_SUFFIXES = {".pyc", ".pyo"}

REQUIRED_RELEASE_FILES = {
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "project_manifest.json",
    "Dockerfile",
    "docker-compose.yml",
    "run.sh",
    "run.bat",
    "app.py",
    "settings.py",
    "docs/api/API_REFERENCE.md",
    "docs/api/openapi.yaml",
    "docs/review/HONEST_LIMITATIONS.md",
    "docs/review/FINAL_REVIEW_CHECKLIST.md",
    "docs/quality/RELEASE_IDENTITY.md",
    "docs/quality/RELEASE_ARTIFACT.md",
    "scripts/validate_project.py",
    "scripts/check_release_artifact.py",
    "scripts/check_release_zip.py",
    "scripts/clean_release_artifacts.py",
    "scripts/check_ci_workflow.py",
    "docs/quality/RELEASE_ZIP.md",
    "docs/quality/RELEASE_WORKSPACE.md",
    "docs/quality/CI_WORKFLOW.md",
    "docs/quality/FILE_INVENTORY.md",
    "docs/release/FILE_INVENTORY.json",
    "scripts/check_file_inventory.py",
    "docs/quality/FINAL_HANDOFF.md",
    "docs/quality/ROUTE_HYGIENE.md",
    "docs/quality/MANIFEST_HYGIENE.md",
    "scripts/final_handoff_check.py",
    "scripts/check_route_hygiene.py",
    "scripts/check_manifest_hygiene.py",
    "docs/quality/VALIDATION_HYGIENE.md",
    "scripts/check_validation_hygiene.py",
    "scripts/run_clean_validation.py",
    "docs/quality/PUBLICATION_HYGIENE.md",
    "scripts/check_publication_hygiene.py",
    CURRENT_RELEASE_NOTE,
}


@dataclass(frozen=True)
class ArtifactCheck:
    name: str
    ok: bool
    detail: Any
    severity: str = "error"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ok": self.ok,
            "detail": self.detail,
            "severity": self.severity,
        }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _is_workspace_local_path(rel: Path) -> bool:
    """Return True for local tooling folders that are not part of release review.

    Reviewers commonly create a virtual environment in the project root exactly
    as the README shows.  The release artifact checker should not fail merely
    because `.venv/` exists in the workspace; ZIP inspection and build scripts
    still reject or exclude virtualenv folders from handoff archives.
    """
    return any(part in WORKSPACE_LOCAL_PATH_PARTS for part in rel.parts)


def _iter_release_paths(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        kept_dirs = []
        for dirname in dirnames:
            child = current / dirname
            rel = child.relative_to(root)
            if _is_workspace_local_path(rel):
                continue
            kept_dirs.append(dirname)
            yield child, rel
        dirnames[:] = kept_dirs
        for filename in filenames:
            path = current / filename
            rel = path.relative_to(root)
            if _is_workspace_local_path(rel):
                continue
            yield path, rel


def _relative_files(root: Path) -> list[Path]:
    return [rel for path, rel in _iter_release_paths(root) if path.is_file()]


def _blocked_artifacts(root: Path) -> list[str]:
    findings: list[str] = []
    for path, rel in _iter_release_paths(root):
        if any(part in BLOCKED_PATH_PARTS for part in rel.parts):
            findings.append(rel.as_posix())
            continue
        if path.is_file() and path.suffix.lower() in BLOCKED_SUFFIXES:
            findings.append(rel.as_posix())
    return sorted(set(findings))


def _generated_runtime_artifacts(root: Path) -> list[str]:
    findings: list[str] = []
    for path, rel in _iter_release_paths(root):
        if any(part in GENERATED_RUNTIME_PATH_PARTS for part in rel.parts):
            findings.append(rel.as_posix())
            continue
        if path.is_file() and path.suffix.lower() in GENERATED_RUNTIME_SUFFIXES:
            findings.append(rel.as_posix())
    return sorted(set(findings))


def _cache_artifacts(root: Path) -> list[str]:
    findings: list[str] = []
    for path, rel in _iter_release_paths(root):
        if any(part in CACHE_PATH_PARTS for part in rel.parts):
            findings.append(rel.as_posix())
            continue
        if path.is_file() and path.suffix.lower() in CACHE_SUFFIXES:
            findings.append(rel.as_posix())
    return sorted(set(findings))


def _zip_files_inside_release(root: Path) -> list[str]:
    return sorted(rel.as_posix() for path, rel in _iter_release_paths(root) if path.is_file() and path.suffix.lower() == ".zip")


def _run_script_hygiene(root: Path) -> dict[str, Any]:
    run_sh = root / "run.sh"
    run_bat = root / "run.bat"
    return {
        "run_sh_exists": run_sh.exists(),
        "run_sh_has_shebang": run_sh.exists() and run_sh.read_text(encoding="utf-8", errors="ignore").startswith("#!"),
        "run_bat_exists": run_bat.exists(),
        "run_bat_mentions_app": run_bat.exists() and "app.py" in run_bat.read_text(encoding="utf-8", errors="ignore"),
    }


def run_release_artifact_check(*, app_root: Path, app_version: str) -> dict[str, Any]:
    """Return release packaging hygiene checks for the current source tree."""
    manifest = _read_json(app_root / "project_manifest.json")
    files = {path.as_posix() for path in _relative_files(app_root)}
    missing = sorted(REQUIRED_RELEASE_FILES - files)
    blocked = _blocked_artifacts(app_root)
    generated_runtime = _generated_runtime_artifacts(app_root)
    cache = _cache_artifacts(app_root)
    nested_zips = _zip_files_inside_release(app_root)
    script_hygiene = _run_script_hygiene(app_root)

    release_notes = manifest.get("release_notes", []) if isinstance(manifest.get("release_notes"), list) else []
    included_docs = manifest.get("included_final_docs", []) if isinstance(manifest.get("included_final_docs"), list) else []

    checks = [
        ArtifactCheck(
            "release_version_matches_app",
            app_version == CURRENT_VERSION and manifest.get("version") == CURRENT_VERSION,
            {"app_version": app_version, "manifest_version": manifest.get("version"), "expected": CURRENT_VERSION},
        ),
        ArtifactCheck(
            "required_release_files_present",
            not missing,
            {"missing": missing},
        ),
        ArtifactCheck(
            "blocked_handoff_artifacts_absent",
            not blocked,
            {"blocked_artifacts": blocked[:50], "count": len(blocked)},
        ),
        ArtifactCheck(
            "generated_runtime_artifacts_reported",
            not generated_runtime,
            {"generated_runtime_artifacts": generated_runtime[:50], "count": len(generated_runtime)},
            severity="warning",
        ),
        ArtifactCheck(
            "cache_artifacts_absent_from_handoff",
            not cache,
            {"cache_artifacts": cache[:50], "count": len(cache)},
            severity="warning",
        ),
        ArtifactCheck(
            "nested_zip_files_absent",
            not nested_zips,
            {"nested_zip_files": nested_zips},
        ),
        ArtifactCheck(
            "run_scripts_are_present_and_clear",
            all(script_hygiene.values()),
            script_hygiene,
        ),
        ArtifactCheck(
            "current_release_note_is_packaged",
            CURRENT_RELEASE_NOTE in files and release_notes.count(CURRENT_RELEASE_NOTE) == 1,
            {"release_note": CURRENT_RELEASE_NOTE, "manifest_count": release_notes.count(CURRENT_RELEASE_NOTE)},
        ),
        ArtifactCheck(
            "manifest_declares_release_review_docs",
            "docs/quality/RELEASE_ARTIFACT.md" in included_docs
            and "docs/quality/FILE_INVENTORY.md" in included_docs
            and "docs/quality/MANIFEST_HYGIENE.md" in included_docs,
            {
                "included_final_docs_contains_release_artifact": "docs/quality/RELEASE_ARTIFACT.md" in included_docs,
                "included_final_docs_contains_file_inventory": "docs/quality/FILE_INVENTORY.md" in included_docs,
                "included_final_docs_contains_manifest_hygiene": "docs/quality/MANIFEST_HYGIENE.md" in included_docs,
            },
        ),
        ArtifactCheck(
            "simulation_boundary_declared_in_manifest",
            bool(manifest.get("safe_mode"))
            and bool(manifest.get("simulation_mode"))
            and not manifest.get("real_packet_capture_enabled")
            and not manifest.get("real_packet_send_enabled")
            and not manifest.get("real_network_scan_enabled"),
            {
                "safe_mode": manifest.get("safe_mode"),
                "simulation_mode": manifest.get("simulation_mode"),
                "real_packet_capture_enabled": manifest.get("real_packet_capture_enabled"),
                "real_packet_send_enabled": manifest.get("real_packet_send_enabled"),
                "real_network_scan_enabled": manifest.get("real_network_scan_enabled"),
            },
        ),
    ]
    items = [check.to_dict() for check in checks]
    failures = [item for item in items if not item["ok"] and item["severity"] == "error"]
    warnings = [item for item in items if not item["ok"] and item["severity"] == "warning"]
    return {
        "status": "pass" if not failures else "fail",
        "version": CURRENT_VERSION,
        "mode": "safe_simulation",
        "summary": {
            "total": len(items),
            "passed": sum(1 for item in items if item["ok"]),
            "warnings": len(warnings),
            "failures": len(failures),
            "file_count": len(files),
        },
        "checks": items,
    }
