"""Capability boundary declaration and static validation.

This module is intentionally explicit about what IPv6 Sentinel Safe can and
cannot do. It helps reviewers avoid overstating the project as a live IDS,
packet sniffer, scanner, or attack tool. The checks are static and read-only:
they inspect local files only and never open sockets, capture packets, scan
networks, or transmit packets.
"""
from __future__ import annotations

import ast
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

CURRENT_VERSION = "27.0.0-safe"

SUPPORTED_CAPABILITIES = (
    "local_dashboard",
    "simulated_ipv6_events",
    "sample_asset_inventory",
    "demo_scenario_seed",
    "csv_json_exports",
    "read_only_release_validation",
)

EXPLICIT_NON_CAPABILITIES = (
    "real_packet_capture",
    "real_packet_transmission",
    "real_network_scanning",
    "dhcpv6_spoofing",
    "dns_spoofing",
    "mitm_operation",
    "ids_ips_detection_coverage",
)

FORBIDDEN_IMPORT_ROOTS = {"scapy", "mitmproxy", "wmi", "netfilterqueue", "pcapy"}
REQUIRED_BOUNDARY_PHRASES = (
    "simulation-only",
    "does not capture packets",
    "does not scan",
    "does not send packets",
)


@dataclass(frozen=True)
class CapabilityCheck:
    name: str
    ok: bool
    detail: Any

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


def capability_boundary_payload() -> dict[str, Any]:
    return {
        "status": "pass",
        "version": CURRENT_VERSION,
        "mode": "safe_simulation",
        "supported_capabilities": list(SUPPORTED_CAPABILITIES),
        "explicit_non_capabilities": list(EXPLICIT_NON_CAPABILITIES),
        "boundary_flags": {
            "safe_mode": True,
            "simulation_mode": True,
            "real_packet_capture_enabled": False,
            "real_packet_send_enabled": False,
            "real_network_scan_enabled": False,
        },
        "reviewer_warning": (
            "This package is a local educational simulator. It must not be described "
            "as a live IPv6 IDS, sniffer, scanner, or network security product."
        ),
    }


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def _load_manifest(root: Path) -> dict[str, Any]:
    try:
        return json.loads((root / "project_manifest.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def _iter_python_files(root: Path) -> Iterable[Path]:
    skip_parts = {".venv", "venv", "env", ".testvenv", "node_modules", "__pycache__"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in skip_parts]
        current = Path(dirpath)
        for filename in filenames:
            if filename.endswith(".py"):
                yield current / filename


def _blocked_import_hits(root: Path) -> list[str]:
    hits: list[str] = []
    for path in _iter_python_files(root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            hits.append(f"{path.relative_to(root).as_posix()} could not be parsed")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name.split(".", 1)[0]
                    if name in FORBIDDEN_IMPORT_ROOTS:
                        hits.append(f"{path.relative_to(root).as_posix()} imports {name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                name = node.module.split(".", 1)[0]
                if name in FORBIDDEN_IMPORT_ROOTS:
                    hits.append(f"{path.relative_to(root).as_posix()} imports {name}")
    return hits


def run_capability_boundary_check(*, app_root: Path, app_version: str) -> dict[str, Any]:
    manifest = _load_manifest(app_root)
    api_reference = _read(app_root / "docs/api/API_REFERENCE.md")
    openapi = _read(app_root / "docs/api/openapi.yaml")
    readme = _read(app_root / "README.md")
    limitations = _read(app_root / "docs/review/HONEST_LIMITATIONS.md")
    capability_doc = _read(app_root / "docs/quality/CAPABILITY_BOUNDARY.md")
    docs_blob = "\n".join([readme, limitations, capability_doc]).lower()

    endpoints = set(str(item) for item in manifest.get("api_endpoints", []))
    reviewer_exports = set(str(item) for item in manifest.get("reviewer_exports", []))
    quality_gates = "\n".join(str(item) for item in manifest.get("quality_gates", []))

    checks = [
        CapabilityCheck(
            "capability_version_matches_app",
            app_version == CURRENT_VERSION,
            {"app_version": app_version, "expected": CURRENT_VERSION},
        ),
        CapabilityCheck(
            "manifest_declares_safe_simulation_boundary",
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
        ),
        CapabilityCheck(
            "no_forbidden_network_tool_imports",
            not _blocked_import_hits(app_root),
            _blocked_import_hits(app_root)[:20],
        ),
        CapabilityCheck(
            "capabilities_endpoint_is_documented",
            "/api/capabilities" in endpoints
            and "/api/capabilities" in reviewer_exports
            and "/api/capabilities" in api_reference
            and "/api/capabilities" in openapi,
            {
                "in_manifest_api_endpoints": "/api/capabilities" in endpoints,
                "in_reviewer_exports": "/api/capabilities" in reviewer_exports,
                "in_api_reference": "/api/capabilities" in api_reference,
                "in_openapi": "/api/capabilities" in openapi,
            },
        ),
        CapabilityCheck(
            "capability_boundary_doc_present",
            bool(capability_doc.strip()),
            "docs/quality/CAPABILITY_BOUNDARY.md",
        ),
        CapabilityCheck(
            "capability_boundary_phrases_visible",
            all(phrase in docs_blob for phrase in REQUIRED_BOUNDARY_PHRASES),
            {"required_phrases": list(REQUIRED_BOUNDARY_PHRASES)},
        ),
        CapabilityCheck(
            "manifest_quality_gates_include_capability_boundary",
            "capability boundary" in quality_gates.lower(),
            "quality_gates should mention capability boundary",
        ),
    ]
    items = [check.to_dict() for check in checks]
    failures = [item for item in items if not item["ok"]]
    payload = capability_boundary_payload()
    payload.update({
        "status": "pass" if not failures else "fail",
        "summary": {"total": len(items), "passed": len(items) - len(failures), "failures": len(failures)},
        "checks": items,
    })
    return payload
