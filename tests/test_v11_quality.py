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

try:
    from app import IPv6SentinelApp
except ModuleNotFoundError as exc:
    IPv6SentinelApp = None  # type: ignore[assignment]
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


class V11QualityPackagingTests(unittest.TestCase):
    def test_v11_preflight_release_files_exist(self) -> None:
        for path in [
            "RELEASE_NOTES_v11.md",
            "services/preflight.py",
            "scripts/preflight_check.py",
            "docs/operations/PREFLIGHT.md",
        ]:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists(), path)

    def test_preflight_is_documented(self) -> None:
        for path in ["README.md", "docs/api/API_REFERENCE.md", "docs/api/openapi.yaml", "project_manifest.json"]:
            with self.subTest(path=path):
                self.assertIn("/api/preflight", (ROOT / path).read_text(encoding="utf-8"))

    def test_preflight_script_outputs_json(self) -> None:
        completed = run_command(
            [sys.executable, str(ROOT / "scripts" / "preflight_check.py")],
            cwd=str(ROOT),
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")
        self.assertTrue(any(check["name"] == "real_packet_features_disabled" for check in payload["checks"]))


@unittest.skipIf(IPv6SentinelApp is None, f"runtime dependencies are not installed: {IMPORT_ERROR}")
class V11QualityRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ipv6_sentinel_v11_"))
        self.env_patch = patch.dict(os.environ, {"IPV6_SENTINEL_DATA_DIR": str(self.temp_dir)})
        self.env_patch.start()

    def tearDown(self) -> None:
        self.env_patch.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_app_construction_does_not_install_signal_handlers(self) -> None:
        with patch("signal.signal") as signal_mock:
            app = IPv6SentinelApp()
            self.assertFalse(signal_mock.called)
            app.shutdown()

    def test_preflight_endpoint_reports_pass(self) -> None:
        app = IPv6SentinelApp()
        client = app.app.test_client()
        response = client.get("/api/preflight")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")
        app.shutdown()


if __name__ == "__main__":
    unittest.main()
