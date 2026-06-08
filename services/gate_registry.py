"""Central registry for reviewer-facing quality gates.

The project now has many static checks. This module keeps a single read-only
index of those gates so reviewers can see which scripts, docs, and optional API
endpoints belong together. It does not execute the gates, open sockets, scan
networks, capture packets, or send packets.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CURRENT_VERSION = "27.0.0-safe"


@dataclass(frozen=True)
class GateDefinition:
    gate_id: str
    title: str
    script: str
    doc: str
    endpoint: str | None = None
    manifest_token: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.gate_id,
            "title": self.title,
            "script": self.script,
            "doc": self.doc,
            "endpoint": self.endpoint,
            "manifest_token": self.manifest_token or self.gate_id.replace("_", " "),
        }


GATE_REGISTRY: tuple[GateDefinition, ...] = (
    GateDefinition("requirements", "Requirements safety", "scripts/check_requirements.py", "docs/operations/INSTALL_CHECK.md", None, "requirements"),
    GateDefinition("preflight", "Preflight readiness", "scripts/preflight_check.py", "docs/operations/PREFLIGHT.md", "/api/preflight", "preflight"),
    GateDefinition("quality", "Release quality", "scripts/release_audit.py", "docs/quality/QUALITY_GATE.md", "/api/quality", "quality"),
    GateDefinition("api_contract", "API contract", "scripts/check_api_contract.py", "docs/quality/API_CONTRACT.md", "/api/contract", "API contract"),
    GateDefinition("schema_contract", "Schema contract", "scripts/check_schema_contract.py", "docs/quality/SCHEMA_CONTRACT.md", "/api/schema", "schema contract"),
    GateDefinition("release_identity", "Release identity", "scripts/check_release_identity.py", "docs/quality/RELEASE_IDENTITY.md", "/api/release", "release identity"),
    GateDefinition("release_artifact", "Release artifact hygiene", "scripts/check_release_artifact.py", "docs/quality/RELEASE_ARTIFACT.md", "/api/artifact", "release artifact"),
    GateDefinition("release_zip", "Release ZIP hygiene", "scripts/check_release_zip.py", "docs/quality/RELEASE_ZIP.md", None, "release ZIP"),
    GateDefinition("ci_workflow", "CI workflow sanity", "scripts/check_ci_workflow.py", "docs/quality/CI_WORKFLOW.md", None, "CI"),
    GateDefinition("file_inventory", "File inventory integrity", "scripts/check_file_inventory.py", "docs/quality/FILE_INVENTORY.md", "/api/integrity", "file inventory"),
    GateDefinition("final_handoff", "Final handoff", "scripts/final_handoff_check.py", "docs/quality/FINAL_HANDOFF.md", None, "final handoff"),
    GateDefinition("release_matrix", "Release matrix", "scripts/check_release_matrix.py", "docs/quality/RELEASE_MATRIX.md", None, "release matrix"),
    GateDefinition("route_hygiene", "Route hygiene", "scripts/check_route_hygiene.py", "docs/quality/ROUTE_HYGIENE.md", None, "route hygiene"),
    GateDefinition("manifest_hygiene", "Manifest hygiene", "scripts/check_manifest_hygiene.py", "docs/quality/MANIFEST_HYGIENE.md", "/api/manifest", "manifest hygiene"),
    GateDefinition("validation_hygiene", "Validation hygiene", "scripts/check_validation_hygiene.py", "docs/quality/VALIDATION_HYGIENE.md", None, "validation hygiene"),
    GateDefinition("publication_hygiene", "Publication hygiene", "scripts/check_publication_hygiene.py", "docs/quality/PUBLICATION_HYGIENE.md", "/api/publication", "publication hygiene"),
    GateDefinition("gate_registry", "Gate registry", "scripts/check_gate_registry.py", "docs/quality/GATE_REGISTRY.md", "/api/gates", "gate registry"),
    GateDefinition("capability_boundary", "Capability boundary", "scripts/check_capability_boundary.py", "docs/quality/CAPABILITY_BOUNDARY.md", "/api/capabilities", "capability boundary"),
    GateDefinition("reviewer_handoff", "Reviewer handoff", "scripts/check_reviewer_handoff.py", "docs/quality/REVIEWER_HANDOFF.md", "/api/reviewer", "reviewer handoff"),
)


def _load_manifest(root: Path) -> dict[str, Any]:
    try:
        return json.loads((root / "project_manifest.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def _check(name: str, ok: bool, detail: Any) -> dict[str, Any]:
    return {"name": name, "ok": ok, "detail": detail}


def gate_registry_payload() -> dict[str, Any]:
    return {
        "status": "pass",
        "version": CURRENT_VERSION,
        "mode": "safe_simulation",
        "gate_count": len(GATE_REGISTRY),
        "gates": [gate.to_dict() for gate in GATE_REGISTRY],
        "notes": [
            "This registry documents release/review gates only.",
            "It does not prove real IPv6 packet capture, packet sending, network scanning, or detection coverage.",
        ],
    }


def run_gate_registry_check(*, app_root: Path, app_version: str) -> dict[str, Any]:
    manifest = _load_manifest(app_root)
    manifest_quality = "\n".join(str(item) for item in manifest.get("quality_gates", []))
    manifest_paths = {str(item) for item in manifest.get("api_endpoints", [])}
    reviewer_exports = {str(item) for item in manifest.get("reviewer_exports", [])}
    api_reference = _read(app_root / "docs/api/API_REFERENCE.md")
    openapi = _read(app_root / "docs/api/openapi.yaml")

    ids = [gate.gate_id for gate in GATE_REGISTRY]
    scripts_missing = [gate.script for gate in GATE_REGISTRY if gate.script and not (app_root / gate.script).exists()]
    docs_missing = [gate.doc for gate in GATE_REGISTRY if gate.doc and not (app_root / gate.doc).exists()]
    endpoints_missing_manifest = [gate.endpoint for gate in GATE_REGISTRY if gate.endpoint and gate.endpoint not in manifest_paths]
    endpoints_missing_review = [gate.endpoint for gate in GATE_REGISTRY if gate.endpoint and gate.endpoint not in reviewer_exports and gate.endpoint in {"/api/gates", "/api/quality", "/api/contract", "/api/schema", "/api/release", "/api/artifact", "/api/integrity", "/api/manifest", "/api/publication", "/api/preflight", "/api/capabilities", "/api/reviewer"}]
    endpoints_missing_docs = [gate.endpoint for gate in GATE_REGISTRY if gate.endpoint and (gate.endpoint not in api_reference or gate.endpoint not in openapi)]
    missing_quality_tokens = [gate.manifest_token or gate.gate_id for gate in GATE_REGISTRY if (gate.manifest_token or gate.gate_id).lower() not in manifest_quality.lower()]

    checks = [
        _check("registry_version_matches_app", app_version == CURRENT_VERSION, {"app_version": app_version, "expected": CURRENT_VERSION}),
        _check("registry_has_unique_ids", len(ids) == len(set(ids)), ids),
        _check("registry_scripts_exist", not scripts_missing, scripts_missing),
        _check("registry_docs_exist", not docs_missing, docs_missing),
        _check("registry_endpoints_declared_in_manifest", not endpoints_missing_manifest, endpoints_missing_manifest),
        _check("reviewer_gate_endpoints_exported", not endpoints_missing_review, endpoints_missing_review),
        _check("registry_endpoints_documented", not endpoints_missing_docs, endpoints_missing_docs),
        _check("manifest_quality_gates_cover_registry", not missing_quality_tokens, missing_quality_tokens),
        _check("safe_simulation_boundary_explicit", bool(manifest.get("safe_mode")) and bool(manifest.get("simulation_mode")) and not manifest.get("real_packet_capture_enabled") and not manifest.get("real_packet_send_enabled") and not manifest.get("real_network_scan_enabled"), "manifest boundary flags"),
    ]
    failures = [check for check in checks if not check["ok"]]
    payload = gate_registry_payload()
    payload.update({
        "status": "pass" if not failures else "fail",
        "summary": {"total": len(checks), "passed": len(checks) - len(failures), "failures": len(failures)},
        "checks": checks,
    })
    return payload
