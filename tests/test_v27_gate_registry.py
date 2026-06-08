from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path

from scripts.check_gate_registry import main as gate_registry_main

ROOT = Path(__file__).resolve().parents[1]


class V27GateRegistryTests(unittest.TestCase):
    def test_gate_registry_script_outputs_pass_json(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exit_code = gate_registry_main()
        self.assertEqual(exit_code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")
        self.assertGreaterEqual(payload["gate_count"], 17)

    def test_gate_registry_endpoint_is_documented(self) -> None:
        api_reference = (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8")
        openapi = (ROOT / "docs/api/openapi.yaml").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("/api/gates", api_reference)
        self.assertIn("/api/gates", openapi)
        self.assertIn("/api/gates", manifest["api_endpoints"])
        self.assertIn("/api/gates", manifest["reviewer_exports"])

    def test_quality_gate_includes_gate_registry(self) -> None:
        quality_gate = (ROOT / "services/quality_gate.py").read_text(encoding="utf-8")
        release_audit = (ROOT / "scripts/release_audit.py").read_text(encoding="utf-8")
        self.assertIn("gate_registry_consistent", quality_gate)
        self.assertIn("run_gate_registry_check", release_audit)


if __name__ == "__main__":
    unittest.main()
