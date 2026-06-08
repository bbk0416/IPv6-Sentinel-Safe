from __future__ import annotations

import json
import unittest
from pathlib import Path

from services.publication_hygiene import run_publication_hygiene_check
from settings import APP_VERSION

ROOT = Path(__file__).resolve().parents[1]


class V27PublicationHygieneTests(unittest.TestCase):
    def test_publication_hygiene_passes_for_clean_source_package(self) -> None:
        payload = run_publication_hygiene_check(app_root=ROOT, app_version=APP_VERSION)
        self.assertEqual(payload["version"], "27.0.0-safe")
        self.assertEqual(payload["status"], "pass")

    def test_publication_endpoint_is_documented(self) -> None:
        self.assertIn("/api/publication", (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8"))
        self.assertIn("/api/publication", (ROOT / "docs/api/openapi.yaml").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("/api/publication", manifest["api_endpoints"])
        self.assertIn("/api/publication", manifest["reviewer_exports"])

    def test_current_release_note_is_v27(self) -> None:
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "27.0.0-safe")
        self.assertEqual(manifest["release_notes"][0], "RELEASE_NOTES_v27.md")
        self.assertEqual(manifest["release_notes"].count("RELEASE_NOTES_v27.md"), 1)
        self.assertTrue((ROOT / "RELEASE_NOTES_v27.md").exists())


if __name__ == "__main__":
    unittest.main()
