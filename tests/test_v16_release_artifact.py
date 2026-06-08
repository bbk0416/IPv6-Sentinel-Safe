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

from services.release_artifact import REQUIRED_RELEASE_FILES, run_release_artifact_check
from settings import APP_VERSION


class V16ReleaseArtifactTests(unittest.TestCase):
    def test_release_artifact_script_outputs_pass_json(self) -> None:
        result = run_command(
            [sys.executable, "scripts/check_release_artifact.py"],
            cwd=ROOT,
            timeout=30,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")

    def test_release_artifact_service_detects_clean_tree(self) -> None:
        payload = run_release_artifact_check(app_root=ROOT, app_version=APP_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["summary"]["failures"], 0)

    def test_release_artifact_service_ignores_local_virtualenv_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "sample"
            root.mkdir()
            for file_name in REQUIRED_RELEASE_FILES:
                target = root / file_name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("placeholder\n", encoding="utf-8")
            (root / "run.sh").write_text("#!/usr/bin/env bash\npython app.py\n", encoding="utf-8")
            (root / "run.bat").write_text("python app.py\n", encoding="utf-8")
            (root / "project_manifest.json").write_text(
                json.dumps({
                    "version": APP_VERSION,
                    "safe_mode": True,
                    "simulation_mode": True,
                    "real_packet_capture_enabled": False,
                    "real_packet_send_enabled": False,
                    "real_network_scan_enabled": False,
                    "release_notes": ["RELEASE_NOTES_v27.md"],
                    "included_final_docs": [
                        "docs/quality/RELEASE_ARTIFACT.md",
                        "docs/quality/FILE_INVENTORY.md",
                        "docs/quality/MANIFEST_HYGIENE.md",
                    ],
                }),
                encoding="utf-8",
            )
            local_cache = root / ".venv" / "lib" / "python" / "site-packages" / "pkg" / "__pycache__"
            local_cache.mkdir(parents=True)
            (local_cache / "module.pyc").write_bytes(b"cache")

            payload = run_release_artifact_check(app_root=root, app_version=APP_VERSION)

            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["summary"]["failures"], 0)

    def test_artifact_endpoint_is_documented(self) -> None:
        openapi = (ROOT / "docs/api/openapi.yaml").read_text(encoding="utf-8")
        api_reference = (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8")
        manifest = (ROOT / "project_manifest.json").read_text(encoding="utf-8")
        self.assertIn("/api/artifact", openapi)
        self.assertIn("/api/artifact", api_reference)
        self.assertIn("/api/artifact", manifest)

    def test_quality_gate_mentions_release_artifact(self) -> None:
        quality = (ROOT / "services/quality_gate.py").read_text(encoding="utf-8")
        validation = (ROOT / "scripts/validate_project.py").read_text(encoding="utf-8")
        self.assertIn("release_artifact_hygiene", quality)
        self.assertIn("check_release_artifact", validation)


class V16ReleaseArtifactRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            import flask  # noqa: F401
            import flask_socketio  # noqa: F401
        except Exception as exc:  # pragma: no cover - dependency optional in source package checks
            self.skipTest(f"runtime dependencies are not installed: {exc}")

    def test_artifact_endpoint_reports_pass(self) -> None:
        from app import IPv6SentinelApp

        temp_dir = Path(tempfile.mkdtemp(prefix="ipv6_sentinel_v16_"))
        with patch.dict(os.environ, {"IPV6_SENTINEL_DATA_DIR": str(temp_dir)}):
            runtime_app = IPv6SentinelApp()
            try:
                client = runtime_app.app.test_client()
                response = client.get("/api/artifact")
                self.assertEqual(response.status_code, 200)
                payload = response.get_json()
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["version"], "27.0.0-safe")
            finally:
                runtime_app.shutdown()
                shutil.rmtree(temp_dir, ignore_errors=True)
