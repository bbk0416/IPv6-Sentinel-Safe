#!/usr/bin/env python3
"""Validate requirements.txt without installing packages.

This check keeps the release package honest: it verifies that the runtime
requirements declare only the simulator dependencies needed for the local web
app and do not reintroduce packet-injection or interception libraries.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "requirements.txt"
REQUIRED = {"flask", "flask-socketio", "python-socketio", "python-engineio", "werkzeug", "psutil", "python-dotenv"}
BLOCKED = {"scapy", "mitmproxy", "wmi", "netfilterqueue", "pcapy", "pypcap"}
PIN_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)")


def _package_names() -> list[str]:
    names: list[str] = []
    for raw in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-e", "git+", "http://", "https://")):
            names.append(line)
            continue
        match = PIN_PATTERN.match(line)
        if match:
            names.append(match.group(1).lower().replace("_", "-"))
    return names


def main() -> int:
    errors: list[str] = []
    if not REQUIREMENTS.exists():
        errors.append("requirements.txt is missing")
        names: list[str] = []
    else:
        names = _package_names()

    installed_names = set(names)
    missing = sorted(REQUIRED - installed_names)
    blocked = sorted(BLOCKED & installed_names)
    unsafe_refs = [name for name in names if name.startswith(("-e", "git+", "http://", "https://"))]

    if missing:
        errors.append("missing required simulator dependencies: " + ", ".join(missing))
    if blocked:
        errors.append("blocked network manipulation dependencies present: " + ", ".join(blocked))
    if unsafe_refs:
        errors.append("direct URL/editable dependencies are not allowed: " + ", ".join(unsafe_refs))

    payload = {
        "status": "pass" if not errors else "fail",
        "dependency_count": len(names),
        "required_present": not missing,
        "blocked_absent": not blocked,
        "direct_references_absent": not unsafe_refs,
        "packages": names,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
