from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
from process_helpers import run_command
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.release_identity import CURRENT_VERSION, run_release_identity_check


class V16ReleaseIdentityTests(unittest.TestCase):
    def test_release_identity_script_outputs_pass_json(self) -> None:
        result = run_command(
            [sys.executable, "scripts/check_release_identity.py"],
            cwd=ROOT,
            timeout=30,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")

    def test_release_identity_service_detects_current_version(self) -> None:
        payload = run_release_identity_check(app_root=ROOT, app_version=CURRENT_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["summary"]["failures"], 0)

    def test_manifest_release_notes_are_unique_and_current(self) -> None:
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        notes = manifest.get("release_notes", [])
        self.assertEqual(notes.count("RELEASE_NOTES_v27.md"), 1)
        self.assertEqual(len(notes), len(set(notes)))

    def test_release_endpoint_is_documented(self) -> None:
        openapi = (ROOT / "docs/api/openapi.yaml").read_text(encoding="utf-8")
        api_reference = (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8")
        manifest = (ROOT / "project_manifest.json").read_text(encoding="utf-8")
        self.assertIn("/api/release", openapi)
        self.assertIn("/api/release", api_reference)
        self.assertIn("/api/release", manifest)
