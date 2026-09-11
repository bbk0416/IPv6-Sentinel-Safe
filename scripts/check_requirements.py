#!/usr/bin/env python3
"""Validate runtime dependency manifests and the container lock without installing packages."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "requirements.txt"
CONTAINER_REQUIREMENTS = ROOT / "requirements-container.txt"
CONTAINER_LOCK = ROOT / "requirements-container.lock"
DOCKERFILE = ROOT / "Dockerfile"
REQUIRED = {"flask", "flask-socketio", "python-socketio", "python-engineio", "werkzeug", "psutil", "python-dotenv"}
CONTAINER_REQUIRED = {"gunicorn", "simple-websocket"}
BLOCKED = {"scapy", "mitmproxy", "wmi", "netfilterqueue", "pcapy", "pypcap"}
NAME_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)")
EXACT_PIN_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s#]+)$")
LOCK_SOURCE_PATTERN = re.compile(r"^# Generated from ([^ ]+) sha256=([0-9a-f]{64})$")
DOCKER_BASE_PATTERN = re.compile(r"^FROM\s+python:3\.12\.14-slim-bookworm@sha256:([0-9a-f]{64})$")


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


def _lock_packages(path: Path) -> tuple[dict[str, str], list[str], dict[str, str]]:
    packages: dict[str, str] = {}
    invalid: list[str] = []
    sources: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        source_match = LOCK_SOURCE_PATTERN.match(line)
        if source_match:
            sources[source_match.group(1)] = source_match.group(2)
            continue
        if line.startswith("#"):
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
    return packages, invalid, sources


def _normalized_sha256(path: Path) -> str:
    normalized = "\n".join(path.read_text(encoding="utf-8").splitlines()) + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


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
        lock_packages, lock_invalid, lock_sources = _lock_packages(CONTAINER_LOCK)
    else:
        lock_packages, lock_invalid, lock_sources = {}, [], {}
        errors.append("requirements-container.lock is missing")

    installed_names = set(names)
    container_installed_names = set(container_names)
    all_manifest_names = installed_names | container_installed_names
    missing = sorted(REQUIRED - installed_names)
    missing_container = sorted(CONTAINER_REQUIRED - container_installed_names)
    blocked = sorted(BLOCKED & all_manifest_names)
    all_unsafe_refs = unsafe_refs + container_unsafe_refs
    missing_from_lock = sorted(all_manifest_names - set(lock_packages))
    lock_only = sorted(set(lock_packages) - all_manifest_names)
    requirements_hash = _normalized_sha256(REQUIREMENTS) if REQUIREMENTS.exists() else ""
    container_requirements_hash = _normalized_sha256(CONTAINER_REQUIREMENTS) if CONTAINER_REQUIREMENTS.exists() else ""
    expected_sources = {
        "requirements.txt": requirements_hash,
        "requirements-container.txt": container_requirements_hash,
    }
    stale_sources = sorted(
        source for source, expected in expected_sources.items() if lock_sources.get(source) != expected
    )
    docker_lines = DOCKERFILE.read_text(encoding="utf-8").splitlines() if DOCKERFILE.exists() else []
    docker_base_lines = [line.strip() for line in docker_lines if line.strip().startswith("FROM ")]
    docker_base_ok = len(docker_base_lines) == 1 and bool(DOCKER_BASE_PATTERN.fullmatch(docker_base_lines[0]))
    docker_installs_lock = any("pip install" in line and "-r requirements-container.lock" in line for line in docker_lines)

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
    if stale_sources:
        errors.append("container dependency lock is stale for: " + ", ".join(stale_sources))
    if not docker_base_ok:
        errors.append("Dockerfile must pin python:3.12.14-slim-bookworm by immutable sha256 digest")
    if not docker_installs_lock:
        errors.append("Dockerfile must install requirements-container.lock")

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
        "container_lock_manifest_hashes_match": not stale_sources,
        "docker_base_immutable": docker_base_ok,
        "docker_installs_lock": docker_installs_lock,
        "packages": names,
        "container_packages": container_names,
        "container_lock_packages": sorted(lock_packages),
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
