#!/usr/bin/env python3
"""Run the final local handoff gate for the safe simulator package.

The default command is intentionally compact and local-only: it delegates to the
clean validation wrapper so reviewer checks do not leave cache/runtime artifacts.
Use ``--plan`` to print the expanded release checklist that includes inventory
refreshing and temporary ZIP validation. This script does not start packet
capture, send packets, scan a network, or contact external services.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

PLAN = [
    {"name": "clean_workspace_before", "command": [PYTHON, "scripts/clean_release_artifacts.py"]},
    {"name": "check_requirements", "command": [PYTHON, "scripts/check_requirements.py"]},
    {"name": "check_frontend_bindings", "command": [PYTHON, "scripts/check_frontend_bindings.py"]},
    {"name": "source_preflight", "command": [PYTHON, "scripts/preflight_check.py"]},
    {"name": "check_api_contract", "command": [PYTHON, "scripts/check_api_contract.py"]},
    {"name": "check_schema_contract", "command": [PYTHON, "scripts/check_schema_contract.py"]},
    {"name": "check_release_identity", "command": [PYTHON, "scripts/check_release_identity.py"]},
    {"name": "check_release_artifact", "command": [PYTHON, "scripts/check_release_artifact.py"]},
    {"name": "check_route_hygiene", "command": [PYTHON, "scripts/check_route_hygiene.py"]},
    {"name": "check_manifest_hygiene", "command": [PYTHON, "scripts/check_manifest_hygiene.py"]},
    {"name": "check_validation_hygiene", "command": [PYTHON, "scripts/check_validation_hygiene.py"]},
    {"name": "check_publication_hygiene", "command": [PYTHON, "scripts/check_publication_hygiene.py"]},
    {"name": "check_ci_workflow", "command": [PYTHON, "scripts/check_ci_workflow.py"]},
    {"name": "check_capability_boundary", "command": [PYTHON, "scripts/check_capability_boundary.py"]},
    {"name": "check_reviewer_handoff", "command": [PYTHON, "scripts/check_reviewer_handoff.py"]},
    {"name": "release_audit", "command": [PYTHON, "scripts/release_audit.py"]},
    {"name": "refresh_file_inventory", "command": [PYTHON, "scripts/check_file_inventory.py", "--write"]},
    {"name": "check_file_inventory", "command": [PYTHON, "scripts/check_file_inventory.py"]},
]


def planned_steps() -> list[dict[str, Any]]:
    return PLAN + [
        {"name": "build_temp_release_zip", "command": [PYTHON, "scripts/build_release.py", "--output", "<temp>/IPv6Sentinel_SAFE_v27_handoff.zip"]},
        {"name": "check_temp_release_zip", "command": [PYTHON, "scripts/check_release_zip.py", "<temp>/IPv6Sentinel_SAFE_v27_handoff.zip"]},
        {"name": "clean_workspace_after", "command": [PYTHON, "scripts/clean_release_artifacts.py"]},
    ]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    # Prevent validation itself from creating cache artifacts that then pollute a
    # release handoff check.
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _run(step: dict[str, Any]) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            step["command"],
            cwd=ROOT,
            env=_env(),
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return {
            "name": step["name"],
            "command": " ".join(step["command"]),
            "returncode": 124,
            "ok": False,
            "stdout_tail": "",
            "stderr_tail": "timeout",
        }
    return {
        "name": step["name"],
        "command": " ".join(step["command"]),
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout_tail": "",
        "stderr_tail": "",
    }


def run_handoff(*, include_unittests: bool = False) -> dict[str, Any]:
    """Run a compact final handoff gate.

    This delegates detailed package validation to `run_clean_validation.py`.
    ZIP validation remains available as `scripts/check_release_zip.py` and is
    included in the documented `--plan` for reviewers.
    """
    steps = [
        {"name": "clean_validation", "command": [PYTHON, "scripts/run_clean_validation.py"]},
    ]
    if include_unittests:
        steps.append({"name": "focused_unittest_subset", "command": [PYTHON, "-m", "unittest", "tests.test_packaging", "tests.test_static_safety", "tests.test_v27_publication_hygiene", "tests.test_v27_reviewer_handoff", "-q"]})
    results: list[dict[str, Any]] = []
    for step in steps:
        result = _run(step)
        results.append(result)
        if not result["ok"]:
            break
    failed = [item for item in results if not item["ok"]]
    return {
        "status": "pass" if not failed else "fail",
        "version": "27.0.0-safe",
        "mode": "safe_simulation",
        "summary": {"total": len(results), "passed": len(results) - len(failed), "failures": len(failed)},
        "checks": results,
        "notes": [
            "This is a final package handoff gate, not a real network detection test.",
            "The project remains a local simulator with no packet capture, no packet sending, and no network scanning.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run final handoff checks for IPv6 Sentinel Safe.")
    parser.add_argument("--plan", action="store_true", help="Print the planned handoff steps without running them.")
    parser.add_argument("--with-tests", action="store_true", help="Also run a focused unittest handoff subset as part of the compact gate.")
    args = parser.parse_args()

    if args.plan:
        print(json.dumps({"status": "plan", "version": "27.0.0-safe", "steps": planned_steps()}, ensure_ascii=False, indent=2))
        return 0

    payload = run_handoff(include_unittests=args.with_tests)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
