#!/usr/bin/env python3
"""Validate the current data-contract schemas without runtime dependencies."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.schemas import SCHEMAS, SCHEMA_CONTRACT_VERSION, schema_contract_payload, validate_payload
from services.state import MonitoringStats
from models.target_manager import Target
from services.simulation_catalog import DEFAULT_UI_SETTINGS


def _sample_log() -> dict:
    return {
        "timestamp": "2026-01-01 00:00:00",
        "event_type": "dns_observed",
        "asset": "sample-client",
        "status": "info",
        "message": "sample observation",
        "details": {"safe_mode": True},
    }


def main() -> int:
    samples = {
        "stats": MonitoringStats().to_dict(),
        "asset": Target(mac="02:00:00:00:00:01", host="sample-client", ipv4="192.0.2.10", ipv6="2001:db8::10").to_dict(),
        "log": _sample_log(),
        "settings": dict(DEFAULT_UI_SETTINGS),
    }
    errors: list[str] = []
    for name in SCHEMAS:
        if name not in samples:
            errors.append(f"missing validation sample for schema: {name}")
            continue
        errors.extend(validate_payload(name, samples[name]))
    payload = schema_contract_payload()
    if payload.get("version") != SCHEMA_CONTRACT_VERSION:
        errors.append("schema contract version mismatch")
    result = {
        "status": "pass" if not errors else "fail",
        "version": SCHEMA_CONTRACT_VERSION,
        "schema_count": len(SCHEMAS),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
