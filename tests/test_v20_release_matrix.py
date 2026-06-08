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

from services.release_matrix import check_release_matrix


class V20ReleaseMatrixTests(unittest.TestCase):
    def test_release_matrix_service_passes(self):
        result = check_release_matrix(ROOT)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["version"], "27.0.0-safe")

    def test_release_matrix_script_outputs_json(self):
        proc = run_command(
            [sys.executable, "scripts/check_release_matrix.py"],
            cwd=ROOT,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")

    def test_v20_release_docs_exist(self):
        self.assertTrue((ROOT / "RELEASE_NOTES_v27.md").exists())
        self.assertTrue((ROOT / "docs/quality/RELEASE_MATRIX.md").exists())
