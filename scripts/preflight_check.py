#!/usr/bin/env python3
"""Run local preflight checks without starting the web server."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.preflight import run_preflight_checks
from settings import (
    APP_VERSION,
    FLASK_HOST,
    FLASK_PORT,
    REAL_NETWORK_SCAN_ENABLED,
    REAL_PACKET_CAPTURE_ENABLED,
    REAL_PACKET_SEND_ENABLED,
    SAFE_MODE,
    SIMULATION_MODE,
    SOCKETIO_CORS_ALLOWED_ORIGINS,
    WEB_AUTH_ENABLED,
    WEB_AUTH_PASSWORD,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run IPv6 Sentinel Safe preflight checks without starting the web server.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat missing runtime dependencies as blocking errors; use after pip install -r requirements.txt",
    )
    args = parser.parse_args()

    result = run_preflight_checks(
        app_root=ROOT,
        app_version=APP_VERSION,
        safe_mode=SAFE_MODE,
        simulation_mode=SIMULATION_MODE,
        real_packet_flags={
            "capture": REAL_PACKET_CAPTURE_ENABLED,
            "send": REAL_PACKET_SEND_ENABLED,
            "scan": REAL_NETWORK_SCAN_ENABLED,
        },
        host=FLASK_HOST,
        port=FLASK_PORT,
        auth_enabled=WEB_AUTH_ENABLED,
        auth_password_set=bool(WEB_AUTH_PASSWORD),
        cors_origins=SOCKETIO_CORS_ALLOWED_ORIGINS,
        dependency_severity="error" if args.strict else "warning",
        profile="runtime" if args.strict else "source_package",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
