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


class V21RouteHygieneTests(unittest.TestCase):
    def test_route_hygiene_script_outputs_pass_json(self) -> None:
        proc = run_command(
            [sys.executable, str(ROOT / "scripts" / "check_route_hygiene.py")],
            cwd=ROOT,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")
        self.assertEqual(payload["duplicate_routes"], [])

    def test_route_hygiene_docs_are_present_and_honest(self) -> None:
        doc = (ROOT / "docs/quality/ROUTE_HYGIENE.md").read_text(encoding="utf-8")
        self.assertIn("27.0.0-safe", doc)
        self.assertIn("no packet capture", doc.lower())
        self.assertIn("no packet sending", doc.lower())
        self.assertIn("no real network scanning", doc.lower())

    def test_release_note_and_manifest_declare_route_hygiene(self) -> None:
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "27.0.0-safe")
        self.assertEqual(manifest["release_notes"].count("RELEASE_NOTES_v27.md"), 1)
        self.assertIn("docs/quality/ROUTE_HYGIENE.md", manifest["included_final_docs"])


if __name__ == "__main__":
    unittest.main()
