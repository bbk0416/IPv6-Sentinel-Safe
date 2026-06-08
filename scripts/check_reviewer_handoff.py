#!/usr/bin/env python3
"""Validate reviewer handoff docs/API metadata without running the server."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.reviewer_handoff import run_reviewer_handoff_check
from settings import APP_VERSION


def main() -> int:
    payload = run_reviewer_handoff_check(app_root=ROOT, app_version=APP_VERSION)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
