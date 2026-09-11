#!/usr/bin/env python3
"""Validate base and container runtime dependency manifests without installing packages."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "requirements.txt"
CONTAINER_REQUIREMENTS = ROOT / "requirements-container.txt"
REQUIRED = {"flask", "flask-socketio", "python-socketio", "python-engineio", "werkzeug", "psutil", "python-dotenv"}
CONTAINER_REQUIRED = {"gunicorn", "simple-websocket"}
BLOCKED = {"scapy", "mitmproxy", "wmi", "netfilterqueue", "pcapy", "pypcap"}
PIN_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)")


def _package_names(path: Path) -> tuple[list[str], list[str]]:
    names: list[str] = []
    unsafe_refs: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-r "):
            continue
        if line.startswith(("-e", "git+", "http://", "https://")):
            unsafe_refs.append(line)
            continue
        match = PIN_PATTERN.match(line)
        if match:
            names.append(match.group(1).lower().replace("_", "-"))
    return names, unsafe_refs


def main() -> int:
    errors: list[str] = []

    if REQUIREMENTS.exists():
        names, unsafe_refs = _package_names(REQUIREMENTS)
    else:
        names, unsafe_refs = [], []
        errors.append("requirements.txt is missing")

    if CONTAINER_REQUIREMENTS.exists():
        container_names, container_unsafe_refs = _package_names(CONTAINER_REQUIREMENTS)
    else:
        container_names, container_unsafe_refs = [], []
        errors.append("requirements-container.txt is missing")

    installed_names = set(names)
    container_installed_names = set(container_names)
    missing = sorted(REQUIRED - installed_names)
    missing_container = sorted(CONTAINER_REQUIRED - container_installed_names)
    blocked = sorted(BLOCKED & (installed_names | container_installed_names))
    all_unsafe_refs = unsafe_refs + container_unsafe_refs

    if missing:
        errors.append("missing required simulator dependencies: " + ", ".join(missing))
    if missing_container:
        errors.append("missing required container dependencies: " + ", ".join(missing_container))
    if blocked:
        errors.append("blocked network manipulation dependencies present: " + ", ".join(blocked))
    if all_unsafe_refs:
        errors.append("direct URL/editable dependencies are not allowed: " + ", ".join(all_unsafe_refs))

    payload = {
        "status": "pass" if not errors else "fail",
        "dependency_count": len(names),
        "container_dependency_count": len(container_names),
        "required_present": not missing,
        "container_required_present": not missing_container,
        "blocked_absent": not blocked,
        "direct_references_absent": not all_unsafe_refs,
        "packages": names,
        "container_packages": container_names,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
