#!/usr/bin/env python3
"""Validate runtime dependency manifests and the container lock without installing packages."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "requirements.txt"
CONTAINER_REQUIREMENTS = ROOT / "requirements-container.txt"
CONTAINER_LOCK = ROOT / "requirements-container.lock"
REQUIRED = {"flask", "flask-socketio", "python-socketio", "python-engineio", "werkzeug", "psutil", "python-dotenv"}
CONTAINER_REQUIRED = {"gunicorn", "simple-websocket"}
BLOCKED = {"scapy", "mitmproxy", "wmi", "netfilterqueue", "pcapy", "pypcap"}
NAME_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)")
EXACT_PIN_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s#]+)$")


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
        match = NAME_PATTERN.match(line)
        if match:
            names.append(match.group(1).lower().replace("_", "-"))
    return names, unsafe_refs


def _lock_packages(path: Path) -> tuple[dict[str, str], list[str]]:
    packages: dict[str, str] = {}
    invalid: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = EXACT_PIN_PATTERN.match(line)
        if not match:
            invalid.append(line)
            continue
        name = match.group(1).lower().replace("_", "-")
        if name in packages:
            invalid.append(f"duplicate:{name}")
            continue
        packages[name] = match.group(2)
    return packages, invalid


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

    if CONTAINER_LOCK.exists():
        lock_packages, lock_invalid = _lock_packages(CONTAINER_LOCK)
    else:
        lock_packages, lock_invalid = {}, []
        errors.append("requirements-container.lock is missing")

    installed_names = set(names)
    container_installed_names = set(container_names)
    missing = sorted(REQUIRED - installed_names)
    missing_container = sorted(CONTAINER_REQUIRED - container_installed_names)
    blocked = sorted(BLOCKED & (installed_names | container_installed_names))
    all_unsafe_refs = unsafe_refs + container_unsafe_refs
    missing_from_lock = sorted((installed_names | container_installed_names) - set(lock_packages))
    lock_only = sorted(set(lock_packages) - (installed_names | container_installed_names))

    if missing:
        errors.append("missing required simulator dependencies: " + ", ".join(missing))
    if missing_container:
        errors.append("missing required container dependencies: " + ", ".join(missing_container))
    if blocked:
        errors.append("blocked network manipulation dependencies present: " + ", ".join(blocked))
    if all_unsafe_refs:
        errors.append("direct URL/editable dependencies are not allowed: " + ", ".join(all_unsafe_refs))
    if lock_invalid:
        errors.append("container lock has invalid or duplicate entries: " + ", ".join(lock_invalid))
    if missing_from_lock:
        errors.append("requirements are missing from container lock: " + ", ".join(missing_from_lock))
    if lock_only:
        errors.append("container lock contains undeclared packages: " + ", ".join(lock_only))

    payload = {
        "status": "pass" if not errors else "fail",
        "dependency_count": len(names),
        "container_dependency_count": len(container_names),
        "container_lock_count": len(lock_packages),
        "required_present": not missing,
        "container_required_present": not missing_container,
        "blocked_absent": not blocked,
        "direct_references_absent": not all_unsafe_refs,
        "container_lock_exact_pins": not lock_invalid,
        "container_lock_covers_manifests": not missing_from_lock and not lock_only,
        "packages": names,
        "container_packages": container_names,
        "container_lock_packages": sorted(lock_packages),
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
