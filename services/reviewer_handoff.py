"""Reviewer handoff summary for public portfolio review.

This module keeps the review entry points, safe claims, non-claims, and first-run
commands in one place. It is deliberately read-only and does not start sockets,
scan networks, capture packets, or send packets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CURRENT_VERSION = "27.0.0-safe"

RUNBOOK_COMMANDS = [
    "python -m venv .venv",
    "source .venv/bin/activate  # Windows: .venv\\Scripts\\activate",
    "pip install -r requirements.txt",
    "python scripts/run_clean_validation.py",
    "python app.py",
]

SAFE_CLAIMS = [
    "Local-only Flask/Socket.IO dashboard for simulated IPv6 security events.",
    "Sample asset inventory, demo scenario, CSV export, JSON snapshot, and reviewer reports.",
    "Quality gates document release consistency, package hygiene, API contracts, and simulator boundaries.",
]

NON_CLAIMS = [
    "Does not capture live packets.",
    "Does not transmit packets.",
    "Does not scan real networks.",
    "Does not perform DHCPv6 spoofing, DNS spoofing, MITM, IDS, or IPS operations.",
]

REVIEW_ENTRYPOINTS = [
    "/api/ready",
    "/api/info",
    "/api/capabilities",
    "/api/quality",
    "/api/contract",
    "/api/schema",
    "/api/gates",
    "/api/reviewer",
]

REQUIRED_REVIEW_DOCS = [
    "README.md",
    "PORTFOLIO_SUMMARY.md",
    "docs/review/HONEST_LIMITATIONS.md",
    "docs/demo/QUICK_START_CHECKLIST.md",
    "docs/quality/CAPABILITY_BOUNDARY.md",
    "docs/quality/REVIEWER_HANDOFF.md",
]


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


def reviewer_handoff_payload() -> dict[str, Any]:
    return {
        "status": "pass",
        "version": CURRENT_VERSION,
        "mode": "safe_simulation",
        "reviewer_summary": "Educational IPv6 security event simulator for portfolio review; not a live network security product.",
        "first_run_commands": RUNBOOK_COMMANDS,
        "safe_claims": SAFE_CLAIMS,
        "non_claims": NON_CLAIMS,
        "review_entrypoints": REVIEW_ENTRYPOINTS,
        "recommended_demo_flow": [
            "Open http://127.0.0.1:5000",
            "Click the demo scenario button or call POST /api/demo/scenario",
            "Review /api/capabilities before making any portfolio claims",
            "Export snapshot/report only as simulated evidence",
        ],
    }


def _check(name: str, ok: bool, detail: Any) -> dict[str, Any]:
    return {"name": name, "ok": ok, "detail": detail}


def run_reviewer_handoff_check(*, app_root: Path, app_version: str) -> dict[str, Any]:
    manifest = _load_manifest(app_root)
    api_reference = _read(app_root / "docs/api/API_REFERENCE.md")
    openapi = _read(app_root / "docs/api/openapi.yaml")
    readme = _read(app_root / "README.md")
    docs_missing = [path for path in REQUIRED_REVIEW_DOCS if not (app_root / path).exists()]
    manifest_endpoints = set(str(item) for item in manifest.get("api_endpoints", []))
    reviewer_exports = set(str(item) for item in manifest.get("reviewer_exports", []))
    docs_bundle = "\n".join(_read(app_root / path) for path in REQUIRED_REVIEW_DOCS if (app_root / path).exists())

    checks = [
        _check("handoff_version_matches_app", app_version == CURRENT_VERSION, {"app_version": app_version, "expected": CURRENT_VERSION}),
        _check("review_docs_present", not docs_missing, docs_missing),
        _check("reviewer_endpoint_declared", "/api/reviewer" in manifest_endpoints and "/api/reviewer" in reviewer_exports, {"manifest": "/api/reviewer" in manifest_endpoints, "reviewer_exports": "/api/reviewer" in reviewer_exports}),
        _check("reviewer_endpoint_documented", "/api/reviewer" in api_reference and "/api/reviewer" in openapi, "API reference and OpenAPI should include /api/reviewer"),
        _check("first_run_command_visible", "python scripts/run_clean_validation.py" in readme and "python app.py" in readme, "README should show validation and app start commands"),
        _check("non_claims_visible", all(token.lower() in docs_bundle.lower() for token in ["does not capture", "does not send", "does not scan", "not a live"]), "review docs should make non-claims visible"),
        _check("manifest_mentions_reviewer_handoff", "reviewer handoff" in "\n".join(str(item) for item in manifest.get("quality_gates", [])).lower(), "quality gates should include reviewer handoff"),
    ]
    failures = [check for check in checks if not check["ok"]]
    payload = reviewer_handoff_payload()
    payload.update({
        "status": "pass" if not failures else "fail",
        "summary": {"total": len(checks), "passed": len(checks) - len(failures), "failures": len(failures)},
        "checks": checks,
    })
    return payload
