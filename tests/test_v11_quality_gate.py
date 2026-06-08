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


class V11QualityGatePackagingTests(unittest.TestCase):
    def test_quality_gate_files_and_docs_exist(self) -> None:
        for path in [
            "services/quality_gate.py",
            "scripts/release_audit.py",
            "docs/quality/QUALITY_GATE.md",
            "RELEASE_NOTES_v11.md",
        ]:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists(), path)

    def test_quality_endpoint_is_documented(self) -> None:
        for path in ["README.md", "docs/api/API_REFERENCE.md", "docs/api/openapi.yaml", "project_manifest.json"]:
            with self.subTest(path=path):
                self.assertIn("/api/quality", (ROOT / path).read_text(encoding="utf-8"))

    def test_release_audit_outputs_json(self) -> None:
        completed = run_command(
            [sys.executable, str(ROOT / "scripts" / "release_audit.py")],
            cwd=str(ROOT),
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")
        self.assertTrue(any(check["name"] == "version_declarations_match" for check in payload["checks"]))


if __name__ == "__main__":
    unittest.main()
