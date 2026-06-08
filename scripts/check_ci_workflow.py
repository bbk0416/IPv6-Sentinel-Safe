#!/usr/bin/env python3
"""Lightweight CI workflow sanity checks without requiring PyYAML."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
REQUIRED_COMMANDS = [
    "python scripts/check_requirements.py",
    "python scripts/preflight_check.py --strict",
    "python scripts/check_api_contract.py",
    "python scripts/check_schema_contract.py",
    "python scripts/check_release_identity.py",
    "python scripts/check_release_artifact.py",
    "python scripts/check_file_inventory.py",
    "python scripts/check_manifest_hygiene.py",
    "python scripts/check_validation_hygiene.py",
    "python scripts/check_publication_hygiene.py",
    "python scripts/check_release_zip.py",
    "python scripts/run_clean_validation.py",
]


def check_workflow() -> dict[str, object]:
    errors: list[str] = []
    text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""
    if not text:
        errors.append("CI workflow file is missing or empty")
    for command in REQUIRED_COMMANDS:
        if command not in text:
            errors.append(f"missing CI command: {command}")
    lines = text.splitlines()
    for idx, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if stripped.startswith("run: ") and not stripped.startswith("run: |"):
            current_indent = len(line) - len(line.lstrip(" "))
            next_line = lines[idx + 1]
            if next_line.strip() and (len(next_line) - len(next_line.lstrip(" "))) > current_indent:
                errors.append(f"line {idx + 1}: multi-command run step must use 'run: |'")
    return {"status": "pass" if not errors else "fail", "errors": errors, "checked_commands": len(REQUIRED_COMMANDS)}


def main() -> int:
    payload = check_workflow()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
