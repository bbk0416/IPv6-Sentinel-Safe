from __future__ import annotations

import json
import os
import shutil
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
from process_helpers import run_command
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.schemas import SCHEMAS, schema_contract_payload, validate_payload
from services.state import MonitoringStats
from models.target_manager import Target
from services.simulation_catalog import DEFAULT_UI_SETTINGS


class V14SchemaContractTests(unittest.TestCase):
    def test_schema_payload_declares_expected_contracts(self):
        payload = schema_contract_payload()
        self.assertEqual(payload["version"], "27.0.0-safe")
        self.assertEqual(payload["status"], "pass")
        self.assertIn("stats", payload["schemas"])
        self.assertIn("asset", payload["schemas"])
        self.assertIn("log", payload["schemas"])
        self.assertIn("settings", payload["schemas"])

    def test_schema_validation_accepts_representative_payloads(self):
        samples = {
            "stats": MonitoringStats().to_dict(),
            "asset": Target(mac="02:00:00:00:00:01", host="sample", ipv4="192.0.2.10", ipv6="2001:db8::10").to_dict(),
            "log": {
                "timestamp": "2026-01-01 00:00:00",
                "event_type": "dns_observed",
                "asset": "sample",
                "status": "info",
                "message": "sample observation",
                "details": {"safe_mode": True},
            },
            "settings": dict(DEFAULT_UI_SETTINGS),
        }
        for name in SCHEMAS:
            self.assertEqual(validate_payload(name, samples[name]), [], name)

    def test_schema_contract_script_outputs_pass_json(self):
        result = run_command(
            [sys.executable, "scripts/check_schema_contract.py"],
            cwd=ROOT,
            timeout=30,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")

    def test_schema_endpoint_is_documented(self):
        api_reference = (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8")
        openapi = (ROOT / "docs/api/openapi.yaml").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("/api/schema", api_reference)
        self.assertIn("/api/schema:", openapi)
        self.assertIn("/api/schema", manifest["api_endpoints"])


try:
    from app import IPv6SentinelApp
except Exception as exc:  # pragma: no cover
    IPv6SentinelApp = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


class V14SchemaRuntimeTests(unittest.TestCase):
    def setUp(self):
        if IPv6SentinelApp is None:
            self.skipTest(f"runtime dependencies are not installed: {IMPORT_ERROR}")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ipv6_sentinel_v14_"))
        self.env_patch = patch.dict(os.environ, {"IPV6_SENTINEL_DATA_DIR": str(self.temp_dir)})
        self.env_patch.start()
        self.runtime_app = IPv6SentinelApp()
        self.client = self.runtime_app.app.test_client()

    def tearDown(self):
        if hasattr(self, "runtime_app"):
            self.runtime_app.shutdown()
        if hasattr(self, "env_patch"):
            self.env_patch.stop()
        if hasattr(self, "temp_dir"):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_schema_endpoint_reports_schema_contract(self):
        response = self.client.get("/api/schema")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["version"], "27.0.0-safe")
        self.assertIn("stats", payload["schemas"])

    def test_portfolio_report_includes_schema_contract(self):
        response = self.client.get("/api/report.json")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("schema_contract", payload["safety"])


if __name__ == "__main__":
    unittest.main()
