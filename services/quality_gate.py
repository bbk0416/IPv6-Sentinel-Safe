"""Read-only quality gate checks for release reviewers.

The quality gate is intentionally boring: it checks that the package is honest
about being simulation-only, that version declarations agree, and that release
review files exist. It never opens sockets, scans networks, or sends packets.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from services.api_contract import run_api_contract_check
from services.release_identity import run_release_identity_check
from services.release_artifact import run_release_artifact_check
from services.file_inventory import run_file_inventory_check
from services.schemas import SCHEMAS
from services.release_matrix import check_release_matrix
from services.route_hygiene import run_route_hygiene_check
from services.manifest_hygiene import run_manifest_hygiene_check
from services.validation_hygiene import run_validation_hygiene_check
from services.publication_hygiene import run_publication_hygiene_check
from services.gate_registry import run_gate_registry_check
from services.capability_boundary import run_capability_boundary_check
from services.reviewer_handoff import run_reviewer_handoff_check


REQUIRED_REVIEW_FILES = (
    "README.md",
    "SECURITY.md",
    "PROJECT_COMPLETION_REPORT.md",
    "VALIDATION_REPORT.md",
    "docs/review/HONEST_LIMITATIONS.md",
    "docs/review/FINAL_REVIEW_CHECKLIST.md",
    "docs/quality/QUALITY_GATE.md",
    "docs/api/API_REFERENCE.md",
    "docs/api/openapi.yaml",
    "docs/quality/API_CONTRACT.md",
    "docs/quality/SCHEMA_CONTRACT.md",
    "docs/quality/RELEASE_IDENTITY.md",
    "docs/quality/RELEASE_ARTIFACT.md",
    "docs/quality/RELEASE_ZIP.md",
    "docs/quality/RELEASE_WORKSPACE.md",
    "docs/quality/CI_WORKFLOW.md",
    "docs/quality/FILE_INVENTORY.md",
    "docs/quality/FINAL_HANDOFF.md",
    "docs/quality/RELEASE_MATRIX.md",
    "docs/quality/ROUTE_HYGIENE.md",
    "docs/quality/MANIFEST_HYGIENE.md",
    "docs/quality/VALIDATION_HYGIENE.md",
    "docs/quality/PUBLICATION_HYGIENE.md",
    "docs/quality/GATE_REGISTRY.md",
    "docs/quality/CAPABILITY_BOUNDARY.md",
    "docs/quality/REVIEWER_HANDOFF.md",
    "docs/release/FILE_INVENTORY.json",
    "project_manifest.json",
)

LOCAL_WORKSPACE_DIRS = (".venv", "venv", "env", ".testvenv", "node_modules")
RUNTIME_ARTIFACT_DIRS = ("backup",)
FORBIDDEN_RUNTIME_IMPORTS = ("scapy", "mitmproxy", "wmi")
HONESTY_TOKENS = ("simulation", "simulator", "safe")


@dataclass(frozen=True)
class QualityCheck:
    name: str
    ok: bool
    detail: str
    severity: str = "error"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ok": self.ok,
            "detail": self.detail,
            "severity": self.severity,
        }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def _version_without_suffix(version: str) -> str:
    return version.removesuffix("-safe")


def _manifest(root: Path) -> dict[str, Any]:
    try:
        return json.loads((root / "project_manifest.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def _python_source_text(root: Path) -> str:
    chunks: list[str] = []
    skip_parts = {".venv", "venv", "env", ".testvenv", "node_modules", "__pycache__", "tests", "scripts"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in skip_parts]
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            if not filename.endswith(".py"):
                continue
            if path.name in {"quality_gate.py", "diagnostics.py"}:
                continue
            chunks.append(_read_text(path))
    return "\n".join(chunks)


def summarize_quality(checks: Iterable[QualityCheck]) -> dict[str, Any]:
    items = [check.to_dict() for check in checks]
    failures = [item for item in items if not item["ok"] and item["severity"] == "error"]
    warnings = [item for item in items if not item["ok"] and item["severity"] == "warning"]
    return {
        "status": "pass" if not failures else "fail",
        "summary": {
            "total": len(items),
            "passed": sum(1 for item in items if item["ok"]),
            "warnings": len(warnings),
            "failures": len(failures),
        },
        "checks": items,
    }


def run_quality_gate(*, app_root: Path, app_version: str) -> dict[str, Any]:
    """Return packaging/portfolio quality checks for local review."""
    manifest = _manifest(app_root)
    pyproject = _read_text(app_root / "pyproject.toml")
    openapi = _read_text(app_root / "docs/api/openapi.yaml")
    readme = _read_text(app_root / "README.md")
    limitations = _read_text(app_root / "docs/review/HONEST_LIMITATIONS.md")
    source = _python_source_text(app_root)
    api_contract = run_api_contract_check(app_root=app_root)
    schema_docs = _read_text(app_root / "docs/quality/SCHEMA_CONTRACT.md")
    release_identity = run_release_identity_check(app_root=app_root, app_version=app_version)
    release_artifact = run_release_artifact_check(app_root=app_root, app_version=app_version)
    file_inventory = run_file_inventory_check(app_root=app_root, app_version=app_version)
    release_matrix = check_release_matrix(app_root)
    route_hygiene = run_route_hygiene_check(app_root=app_root, app_version=app_version)
    manifest_hygiene = run_manifest_hygiene_check(app_root=app_root, app_version=app_version)
    validation_hygiene = run_validation_hygiene_check(app_root=app_root, app_version=app_version)
    publication_hygiene = run_publication_hygiene_check(app_root=app_root, app_version=app_version)
    gate_registry = run_gate_registry_check(app_root=app_root, app_version=app_version)
    capability_boundary = run_capability_boundary_check(app_root=app_root, app_version=app_version)
    reviewer_handoff = run_reviewer_handoff_check(app_root=app_root, app_version=app_version)

    missing = [path for path in REQUIRED_REVIEW_FILES if not (app_root / path).exists()]
    runtime_artifacts = [path.name for path in app_root.iterdir() if path.name in RUNTIME_ARTIFACT_DIRS]
    blocked_import_hits = [token for token in FORBIDDEN_RUNTIME_IMPORTS if f"import {token}" in source or f"from {token}" in source]

    clean_version = _version_without_suffix(app_version)
    checks = [
        QualityCheck(
            "version_is_safe_release",
            app_version.endswith("-safe"),
            f"app_version={app_version}",
        ),
        QualityCheck(
            "version_declarations_match",
            manifest.get("version") == app_version
            and f'version = "{clean_version}"' in pyproject
            and f"version: {app_version}" in openapi,
            "settings/manifest/OpenAPI should declare the safe release ID; pyproject should declare the normalized PEP 440 package version.",
        ),
        QualityCheck(
            "review_files_present",
            not missing,
            "missing: " + ", ".join(missing) if missing else "all required review files exist",
        ),
        QualityCheck(
            "runtime_artifacts_excluded_from_release_root",
            not runtime_artifacts,
            "found: " + ", ".join(runtime_artifacts)
            if runtime_artifacts
            else "none; local reviewer virtualenv folders are ignored in source workspaces and excluded from ZIP handoff",
        ),
        QualityCheck(
            "no_forbidden_runtime_imports",
            not blocked_import_hits,
            "blocked imports found: " + ", ".join(blocked_import_hits) if blocked_import_hits else "none",
        ),
        QualityCheck(
            "manifest_declares_simulation_only",
            bool(manifest.get("safe_mode"))
            and bool(manifest.get("simulation_mode"))
            and not manifest.get("real_packet_capture_enabled")
            and not manifest.get("real_packet_send_enabled")
            and not manifest.get("real_network_scan_enabled"),
            "manifest must make the simulator boundary explicit.",
        ),
        QualityCheck(
            "honest_limitations_are_visible",
            all(token in (readme + limitations).lower() for token in HONESTY_TOKENS),
            "README and HONEST_LIMITATIONS should clearly describe the local simulation boundary.",
        ),
        QualityCheck(
            "api_contract_consistent",
            api_contract.get("status") == "pass",
            "Flask routes, OpenAPI, API reference, and manifest should match.",
        ),
        QualityCheck(
            "schema_contract_documented",
            all(name in schema_docs for name in SCHEMAS),
            "Data-contract schemas should be documented for reviewer-facing payloads.",
        ),
        QualityCheck(
            "release_identity_consistent",
            release_identity.get("status") == "pass",
            "Safe release ID and normalized package version should be consistently declared across settings, pyproject, manifest, OpenAPI, and handoff docs.",
        ),
        QualityCheck(
            "release_artifact_hygiene",
            release_artifact.get("status") == "pass",
            "Release package should exclude runtime artifacts and include reviewer handoff files.",
        ),
        QualityCheck(
            "file_inventory_integrity",
            file_inventory.get("status") == "pass",
            "Release file inventory should match the current clean source tree.",
        ),
        QualityCheck(
            "release_matrix_consistent",
            release_matrix.get("status") == "pass",
            "Reviewer-facing version markers should match the current safe release.",
        ),
        QualityCheck(
            "route_hygiene_consistent",
            route_hygiene.get("status") == "pass",
            "Flask route decorators should be unique and REST fallback routes should remain present.",
        ),
        QualityCheck(
            "manifest_hygiene_consistent",
            manifest_hygiene.get("status") == "pass",
            "project_manifest.json should match the current package files, release notes, docs, and exported API paths.",
        ),
        QualityCheck(
            "validation_hygiene_consistent",
            validation_hygiene.get("status") == "pass",
            "Validation commands should clean generated cache artifacts and document the clean validation path.",
        ),
        QualityCheck(
            "publication_hygiene_consistent",
            publication_hygiene.get("status") == "pass",
            "Public handoff package should not include obvious personal markers, private IPs, user paths, stale release markers, or credential patterns.",
        ),
        QualityCheck(
            "gate_registry_consistent",
            gate_registry.get("status") == "pass",
            "Reviewer-facing quality gates should be centrally registered with matching scripts, docs, endpoints, and manifest entries.",
        ),
        QualityCheck(
            "capability_boundary_consistent",
            capability_boundary.get("status") == "pass",
            "Supported and explicitly unsupported capabilities should be declared across source, docs, API, and manifest.",
        ),
        QualityCheck(
            "reviewer_handoff_consistent",
            reviewer_handoff.get("status") == "pass",
            "Reviewer runbook, non-claims, and review entry points should be aligned.",
        ),
    ]
    payload = summarize_quality(checks)
    payload.update({"version": app_version, "mode": "safe_simulation", "release_artifact": release_artifact, "file_inventory": file_inventory, "release_matrix": release_matrix, "route_hygiene": route_hygiene, "manifest_hygiene": manifest_hygiene, "validation_hygiene": validation_hygiene, "publication_hygiene": publication_hygiene, "gate_registry": gate_registry, "capability_boundary": capability_boundary, "reviewer_handoff": reviewer_handoff})
    return payload
