"""Flask route hygiene checks for the safe simulator release.

This module is intentionally static and read-only. It checks that reviewer-facing
Flask route decorators do not accidentally drift into duplicate declarations or
missing REST fallback endpoints. It does not start the web server, capture
packets, send packets, or scan a network.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

CURRENT_VERSION = "27.0.0-safe"

ROUTE_RE = re.compile(r"@self\.app\.route\(\s*[\"']([^\"']+)[\"']")
REQUIRED_REST_FALLBACKS = {
    "/api/monitoring/start",
    "/api/monitoring/stop",
    "/api/assets/generate",
    "/api/logs/clear",
    "/api/simulation/speed",
}


def extract_route_paths(app_py: Path) -> list[str]:
    if not app_py.exists():
        return []
    return ROUTE_RE.findall(app_py.read_text(encoding="utf-8", errors="ignore"))


def run_route_hygiene_check(*, app_root: Path | str = ".", app_version: str = CURRENT_VERSION) -> dict[str, Any]:
    root = Path(app_root)
    routes = extract_route_paths(root / "app.py")
    counts = Counter(routes)
    duplicate_routes = sorted(path for path, count in counts.items() if count > 1)
    missing_fallbacks = sorted(REQUIRED_REST_FALLBACKS - set(routes))
    checks = [
        {
            "name": "flask_route_decorators_present",
            "ok": bool(routes),
            "detail": f"route_count={len(routes)}",
        },
        {
            "name": "no_duplicate_route_decorators",
            "ok": not duplicate_routes,
            "detail": duplicate_routes or "none",
        },
        {
            "name": "rest_fallback_routes_present",
            "ok": not missing_fallbacks,
            "detail": missing_fallbacks or "all REST fallback routes present",
        },
    ]
    failures = [check for check in checks if not check["ok"]]
    return {
        "status": "pass" if not failures else "fail",
        "version": app_version,
        "route_count": len(routes),
        "unique_route_count": len(counts),
        "duplicate_routes": duplicate_routes,
        "checks": checks,
        "summary": {"total": len(checks), "passed": len(checks) - len(failures), "failures": len(failures)},
        "notes": [
            "This is a static route-decorator hygiene check, not a live browser test.",
            "It does not add real IPv6 packet capture, packet sending, or network scanning.",
        ],
    }
