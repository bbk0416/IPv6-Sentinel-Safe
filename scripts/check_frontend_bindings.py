#!/usr/bin/env python3
"""Check that dashboard JavaScript bindings match rendered template IDs and REST APIs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_JS = ROOT / "static" / "dashboard.js"
INDEX_HTML = ROOT / "templates" / "index.html"
APP_PY = ROOT / "app.py"

REQUIRED_REST_ENDPOINTS = {
    "/api/stats",
    "/api/assets",
    "/api/performance",
    "/api/logs",
    "/api/monitoring/start",
    "/api/monitoring/stop",
    "/api/assets/generate",
    "/api/logs/clear",
    "/api/simulation/speed",
    "/api/reset",
    "/api/demo/scenario",
}


def main() -> int:
    dashboard = DASHBOARD_JS.read_text(encoding="utf-8")
    html = INDEX_HTML.read_text(encoding="utf-8")
    app = APP_PY.read_text(encoding="utf-8")

    js_ids = set(re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", dashboard))
    html_ids = set(re.findall(r"id=[\"']([^\"']+)[\"']", html))
    missing_ids = sorted(js_ids - html_ids)

    missing_endpoints = sorted(endpoint for endpoint in REQUIRED_REST_ENDPOINTS if endpoint not in dashboard or endpoint not in app)

    errors = []
    if missing_ids:
        errors.append("missing template IDs used by dashboard.js: " + ", ".join(missing_ids))
    if missing_endpoints:
        errors.append("REST fallback endpoint drift: " + ", ".join(missing_endpoints))
    if "enterRestFallbackMode" not in dashboard:
        errors.append("dashboard.js no longer exposes REST fallback mode")

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1

    print("[OK] frontend bindings match template and REST fallback endpoints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
