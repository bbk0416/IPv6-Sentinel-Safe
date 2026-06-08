#!/usr/bin/env python3
"""Check project_manifest.json hygiene without starting the web server."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.manifest_hygiene import run_manifest_hygiene_check  # noqa: E402
from settings import APP_VERSION  # noqa: E402


def main() -> int:
    payload = run_manifest_hygiene_check(app_root=ROOT, app_version=APP_VERSION)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
