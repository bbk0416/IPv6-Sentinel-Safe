"""Preflight checks for release demos and local execution.

The checks are intentionally read-only. They inspect local settings, Python
version, required files, and safe-mode flags; they never scan networks or send
packets.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REQUIRED_RUNTIME_MODULES = ("flask", "flask_socketio", "psutil")
REQUIRED_REVIEW_FILES = (
    "README.md",
    "SECURITY.md",
    "docs/review/HONEST_LIMITATIONS.md",
    "docs/api/API_REFERENCE.md",
    "docs/api/openapi.yaml",
    "tests/test_app_runtime.py",
    "docs/quality/QUALITY_GATE.md",
    "scripts/release_audit.py",
)


@dataclass(frozen=True)
class PreflightCheck:
    name: str
    ok: bool
    detail: str
    severity: str = "error"

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail, "severity": self.severity}


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _is_loopback_host(host: str) -> bool:
    return (host or "").strip().lower() in {"127.0.0.1", "localhost", "::1"}


def summarize_preflight(checks: Iterable[PreflightCheck]) -> dict[str, Any]:
    items = [check.to_dict() for check in checks]
    blocking_failures = [item for item in items if not item["ok"] and item["severity"] == "error"]
    warnings = [item for item in items if not item["ok"] and item["severity"] == "warning"]
    return {
        "status": "pass" if not blocking_failures else "fail",
        "summary": {
            "total": len(items),
            "passed": sum(1 for item in items if item["ok"]),
            "warnings": len(warnings),
            "failures": len(blocking_failures),
        },
        "checks": items,
    }


def run_preflight_checks(
    *,
    app_root: Path,
    app_version: str,
    safe_mode: bool,
    simulation_mode: bool,
    real_packet_flags: Mapping[str, bool],
    host: str,
    port: int,
    auth_enabled: bool,
    auth_password_set: bool,
    cors_origins: Sequence[str],
    dependency_severity: str = "error",
    profile: str = "runtime",
) -> dict[str, Any]:
    """Return local preflight checks for reviewers and demo operators.

    ``profile="runtime"`` is strict and treats missing runtime modules as
    blocking errors. ``profile="source_package"`` is for reviewers who are
    inspecting the release ZIP before installing dependencies; missing modules
    are reported as warnings so packaging tests can still run honestly.
    """
    module_status = {name: _module_available(name) for name in REQUIRED_RUNTIME_MODULES}
    missing_files = [path for path in REQUIRED_REVIEW_FILES if not (app_root / path).exists()]
    remote_bind = not _is_loopback_host(host)
    wildcard_cors = any(origin == "*" for origin in cors_origins)

    checks = [
        PreflightCheck(
            "python_version_supported",
            sys.version_info >= (3, 10),
            f"running {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}; requires >=3.10",
        ),
        PreflightCheck(
            "runtime_dependencies_available",
            all(module_status.values()),
            "module availability: " + ", ".join(f"{k}={v}" for k, v in module_status.items()),
            severity=dependency_severity if dependency_severity in {"error", "warning"} else "error",
        ),
        PreflightCheck("safe_mode_enabled", bool(safe_mode), "SAFE_MODE must remain true."),
        PreflightCheck("simulation_mode_enabled", bool(simulation_mode), "SIMULATION_MODE must remain true."),
        PreflightCheck(
            "real_packet_features_disabled",
            not any(real_packet_flags.values()),
            f"real packet flags: {dict(real_packet_flags)}",
        ),
        PreflightCheck(
            "bind_is_local_or_authenticated",
            (not remote_bind) or (auth_enabled and auth_password_set),
            f"host={host!r}, port={port}, auth_enabled={auth_enabled}, password_set={auth_password_set}",
        ),
        PreflightCheck(
            "cors_is_not_wildcard",
            not wildcard_cors,
            f"cors_origins={list(cors_origins)}",
        ),
        PreflightCheck(
            "review_files_present",
            not missing_files,
            "missing: " + ", ".join(missing_files) if missing_files else "all required review files exist",
        ),
        PreflightCheck(
            "declared_version_is_safe_release",
            app_version.endswith("-safe"),
            f"version={app_version}",
        ),
    ]
    result = summarize_preflight(checks)
    result.update({"version": app_version, "mode": "safe_simulation", "profile": profile})
    return result
