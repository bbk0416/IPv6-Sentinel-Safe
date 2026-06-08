from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path

from scripts.check_capability_boundary import main as capability_boundary_main
from services.capability_boundary import run_capability_boundary_check
from settings import APP_VERSION

ROOT = Path(__file__).resolve().parents[1]


class V27CapabilityBoundaryTests(unittest.TestCase):
    def test_capability_boundary_script_outputs_pass_json(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exit_code = capability_boundary_main()
        self.assertEqual(exit_code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")
        self.assertIn("real_packet_capture", payload["explicit_non_capabilities"])
        self.assertIn("sample_asset_inventory", payload["supported_capabilities"])

    def test_capability_endpoint_is_documented(self) -> None:
        api_reference = (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8")
        openapi = (ROOT / "docs/api/openapi.yaml").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("/api/capabilities", api_reference)
        self.assertIn("/api/capabilities", openapi)
        self.assertIn("/api/capabilities", manifest["api_endpoints"])
        self.assertIn("/api/capabilities", manifest["reviewer_exports"])

    def test_quality_gate_includes_capability_boundary(self) -> None:
        payload = run_capability_boundary_check(app_root=ROOT, app_version=APP_VERSION)
        quality_gate = (ROOT / "services/quality_gate.py").read_text(encoding="utf-8")
        release_audit = (ROOT / "scripts/release_audit.py").read_text(encoding="utf-8")
        self.assertEqual(payload["status"], "pass")
        self.assertIn("capability_boundary_consistent", quality_gate)
        self.assertIn("run_capability_boundary_check", release_audit)

    def test_current_release_note_is_v27(self) -> None:
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "27.0.0-safe")
        self.assertEqual(manifest["release_notes"][0], "RELEASE_NOTES_v27.md")
        self.assertEqual(manifest["release_notes"].count("RELEASE_NOTES_v27.md"), 1)
        self.assertTrue((ROOT / "RELEASE_NOTES_v27.md").exists())


if __name__ == "__main__":
    unittest.main()
