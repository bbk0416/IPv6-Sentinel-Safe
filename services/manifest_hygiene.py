"""Project manifest hygiene checks for release reviewers.

The manifest is the package's compact map for reviewers.  This module checks
that it is not stale: API paths are unique, listed documents exist, release
notes match the files in the tree, and reviewer exports are declared API paths.
It is static and read-only and never starts the web app or touches the network.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

CURRENT_VERSION = "27.0.0-safe"
CURRENT_RELEASE_NOTE = "RELEASE_NOTES_v27.md"

LIST_FIELDS = (
    "key_features",
    "reviewer_exports",
    "included_final_docs",
    "features",
    "api_endpoints",
    "quality_gates",
    "release_notes",
)

REQUIRED_FINAL_DOCS = {
    "docs/review/FINAL_REVIEW_CHECKLIST.md",
    "docs/review/HONEST_LIMITATIONS.md",
    "docs/quality/MANIFEST_HYGIENE.md",
    "docs/quality/ROUTE_HYGIENE.md",
    "docs/quality/RELEASE_MATRIX.md",
    "docs/quality/FILE_INVENTORY.md",
    "docs/quality/VALIDATION_HYGIENE.md",
    "docs/quality/PUBLICATION_HYGIENE.md",
    "docs/quality/CAPABILITY_BOUNDARY.md",
    "docs/quality/REVIEWER_HANDOFF.md",
}

REQUIRED_QUALITY_GATE_TOKENS = {
    "API contract",
    "schema contract",
    "release identity",
    "release artifact",
    "file inventory",
    "release matrix",
    "route hygiene",
    "manifest hygiene",
    "validation hygiene",
    "publication hygiene",
    "capability boundary",
    "reviewer handoff",
}


@dataclass(frozen=True)
class ManifestCheck:
    name: str
    ok: bool
    detail: Any

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


def _read_manifest(root: Path) -> dict[str, Any]:
    try:
        return json.loads((root / "project_manifest.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def _list(payload: dict[str, Any], field: str) -> list[str]:
    value = payload.get(field, [])
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _duplicates(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    dupes: set[str] = set()
    for item in items:
        if item in seen:
            dupes.add(item)
        seen.add(item)
    return sorted(dupes)


def _release_note_key(path: str) -> int:
    stem = Path(path).stem
    try:
        return int(stem.split("_v", 1)[1])
    except Exception:
        return -1


def run_manifest_hygiene_check(*, app_root: Path, app_version: str) -> dict[str, Any]:
    manifest = _read_manifest(app_root)
    checks: list[ManifestCheck] = []

    checks.append(ManifestCheck(
        "manifest_version_matches_app",
        manifest.get("version") == app_version == CURRENT_VERSION,
        {"manifest_version": manifest.get("version"), "app_version": app_version, "expected": CURRENT_VERSION},
    ))

    duplicates_by_field = {field: _duplicates(_list(manifest, field)) for field in LIST_FIELDS}
    checks.append(ManifestCheck(
        "manifest_lists_have_no_duplicates",
        all(not dupes for dupes in duplicates_by_field.values()),
        {field: dupes for field, dupes in duplicates_by_field.items() if dupes},
    ))

    included_docs = set(_list(manifest, "included_final_docs"))
    missing_included_docs = sorted(path for path in included_docs if not (app_root / path).exists())
    missing_required_docs = sorted(path for path in REQUIRED_FINAL_DOCS if path not in included_docs)
    checks.append(ManifestCheck(
        "included_final_docs_exist_and_cover_hygiene_docs",
        not missing_included_docs and not missing_required_docs,
        {"missing_files": missing_included_docs, "missing_required_manifest_entries": missing_required_docs},
    ))

    api_endpoints = set(_list(manifest, "api_endpoints"))
    reviewer_exports = set(_list(manifest, "reviewer_exports"))
    checks.append(ManifestCheck(
        "reviewer_exports_are_declared_api_endpoints",
        reviewer_exports <= api_endpoints,
        {"missing_from_api_endpoints": sorted(reviewer_exports - api_endpoints)},
    ))

    release_notes = _list(manifest, "release_notes")
    existing_release_notes = sorted(path.name for path in app_root.glob("RELEASE_NOTES_v*.md"))
    checks.append(ManifestCheck(
        "manifest_release_notes_match_tree",
        set(release_notes) == set(existing_release_notes),
        {
            "missing_from_manifest": sorted(set(existing_release_notes) - set(release_notes), key=_release_note_key),
            "extra_in_manifest": sorted(set(release_notes) - set(existing_release_notes), key=_release_note_key),
            "manifest_count": len(release_notes),
            "tree_count": len(existing_release_notes),
        },
    ))
    checks.append(ManifestCheck(
        "current_release_note_is_present",
        release_notes.count(CURRENT_RELEASE_NOTE) == 1 and (app_root / CURRENT_RELEASE_NOTE).exists(),
        {"release_note": CURRENT_RELEASE_NOTE, "manifest_count": release_notes.count(CURRENT_RELEASE_NOTE)},
    ))

    quality_text = "\n".join(_list(manifest, "quality_gates"))
    missing_gate_tokens = sorted(token for token in REQUIRED_QUALITY_GATE_TOKENS if token.lower() not in quality_text.lower())
    checks.append(ManifestCheck(
        "quality_gate_list_mentions_current_gates",
        not missing_gate_tokens,
        {"missing_tokens": missing_gate_tokens},
    ))

    checks.append(ManifestCheck(
        "safe_simulation_boundary_is_explicit",
        bool(manifest.get("safe_mode"))
        and bool(manifest.get("simulation_mode"))
        and manifest.get("real_packet_capture_enabled") is False
        and manifest.get("real_packet_send_enabled") is False
        and manifest.get("real_network_scan_enabled") is False,
        {
            "safe_mode": manifest.get("safe_mode"),
            "simulation_mode": manifest.get("simulation_mode"),
            "real_packet_capture_enabled": manifest.get("real_packet_capture_enabled"),
            "real_packet_send_enabled": manifest.get("real_packet_send_enabled"),
            "real_network_scan_enabled": manifest.get("real_network_scan_enabled"),
        },
    ))

    items = [check.to_dict() for check in checks]
    failures = [item for item in items if not item["ok"]]
    return {
        "status": "pass" if not failures else "fail",
        "version": CURRENT_VERSION,
        "summary": {"total": len(items), "passed": len(items) - len(failures), "failures": len(failures)},
        "checks": items,
    }
