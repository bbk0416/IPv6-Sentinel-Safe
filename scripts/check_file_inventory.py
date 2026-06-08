#!/usr/bin/env python3
"""Check or write the deterministic release file inventory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.file_inventory import INVENTORY_PATH, build_file_inventory, run_file_inventory_check  # noqa: E402
from settings import APP_VERSION  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or refresh the release file inventory.")
    parser.add_argument("--write", action="store_true", help="Write docs/release/FILE_INVENTORY.json for the current tree.")
    args = parser.parse_args()

    if args.write:
        payload = build_file_inventory(ROOT, version=APP_VERSION)
        target = ROOT / INVENTORY_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "written", "path": str(INVENTORY_PATH), "file_count": payload["file_count"], "package_sha256": payload["package_sha256"]}, ensure_ascii=False, indent=2))
        return 0

    payload = run_file_inventory_check(app_root=ROOT, app_version=APP_VERSION)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
