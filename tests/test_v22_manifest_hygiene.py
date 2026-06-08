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


class V22ManifestHygieneTests(unittest.TestCase):
    def test_manifest_hygiene_script_passes(self) -> None:
        proc = run_command(
            [sys.executable, "scripts/check_manifest_hygiene.py"],
            cwd=ROOT,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "pass")

    def test_manifest_declares_all_release_notes(self) -> None:
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        declared = set(manifest.get("release_notes", []))
        actual = {path.name for path in ROOT.glob("RELEASE_NOTES_v*.md")}
        self.assertEqual(declared, actual)
        self.assertIn("RELEASE_NOTES_v27.md", declared)

    def test_manifest_endpoint_is_documented(self) -> None:
        app_text = (ROOT / "app.py").read_text(encoding="utf-8")
        openapi = (ROOT / "docs/api/openapi.yaml").read_text(encoding="utf-8")
        api_ref = (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertIn('/api/manifest', app_text)
        self.assertIn('/api/manifest', openapi)
        self.assertIn('/api/manifest', api_ref)
        self.assertIn('/api/manifest', manifest.get('api_endpoints', []))
        self.assertIn('/api/manifest', manifest.get('reviewer_exports', []))

    def test_manifest_hygiene_doc_is_in_manifest(self) -> None:
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("docs/quality/MANIFEST_HYGIENE.md", manifest.get("included_final_docs", []))
        self.assertTrue((ROOT / "docs/quality/MANIFEST_HYGIENE.md").exists())


if __name__ == "__main__":
    unittest.main()
