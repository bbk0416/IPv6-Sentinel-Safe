#!/usr/bin/env python3
"""Run read-only release quality checks from the command line."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.quality_gate import run_quality_gate  # noqa: E402
from services.release_identity import run_release_identity_check  # noqa: E402
from services.file_inventory import run_file_inventory_check  # noqa: E402
from services.schemas import schema_contract_payload  # noqa: E402
from services.release_matrix import check_release_matrix  # noqa: E402
from services.route_hygiene import run_route_hygiene_check  # noqa: E402
from services.manifest_hygiene import run_manifest_hygiene_check  # noqa: E402
from services.validation_hygiene import run_validation_hygiene_check  # noqa: E402
from services.publication_hygiene import run_publication_hygiene_check  # noqa: E402
from services.gate_registry import run_gate_registry_check  # noqa: E402
from services.capability_boundary import run_capability_boundary_check  # noqa: E402
from services.reviewer_handoff import run_reviewer_handoff_check  # noqa: E402
from settings import APP_VERSION  # noqa: E402


def main() -> int:
    payload = run_quality_gate(app_root=ROOT, app_version=APP_VERSION)
    payload["schema_contract"] = {"status": schema_contract_payload().get("status"), "schema_count": schema_contract_payload().get("schema_count")}
    payload["release_identity"] = run_release_identity_check(app_root=ROOT, app_version=APP_VERSION)
    payload["file_inventory"] = run_file_inventory_check(app_root=ROOT, app_version=APP_VERSION)
    payload["release_matrix"] = check_release_matrix(ROOT)
    payload["route_hygiene"] = run_route_hygiene_check(app_root=ROOT, app_version=APP_VERSION)
    payload["manifest_hygiene"] = run_manifest_hygiene_check(app_root=ROOT, app_version=APP_VERSION)
    payload["validation_hygiene"] = run_validation_hygiene_check(app_root=ROOT, app_version=APP_VERSION)
    payload["publication_hygiene"] = run_publication_hygiene_check(app_root=ROOT, app_version=APP_VERSION)
    payload["gate_registry"] = run_gate_registry_check(app_root=ROOT, app_version=APP_VERSION)
    payload["capability_boundary"] = run_capability_boundary_check(app_root=ROOT, app_version=APP_VERSION)
    payload["reviewer_handoff"] = run_reviewer_handoff_check(app_root=ROOT, app_version=APP_VERSION)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    required_pass = (
        payload["status"] == "pass"
        and payload["release_matrix"].get("status") == "pass"
        and payload["route_hygiene"].get("status") == "pass"
        and payload["manifest_hygiene"].get("status") == "pass"
        and payload["validation_hygiene"].get("status") == "pass"
        and payload["publication_hygiene"].get("status") == "pass"
        and payload["gate_registry"].get("status") == "pass"
        and payload["capability_boundary"].get("status") == "pass"
        and payload["reviewer_handoff"].get("status") == "pass"
    )
    return 0 if required_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
