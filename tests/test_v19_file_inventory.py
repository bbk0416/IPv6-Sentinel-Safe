from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import os
import shutil
import tempfile
import sys
import unittest
from unittest import mock
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class V19FileInventoryTests(unittest.TestCase):
    def test_file_inventory_script_outputs_pass_json(self) -> None:
        script = ROOT / "scripts" / "check_file_inventory.py"
        spec = importlib.util.spec_from_file_location("check_file_inventory", script)
        self.assertIsNotNone(spec)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        buffer = io.StringIO()
        with mock.patch.object(sys, "argv", ["check_file_inventory.py"]), contextlib.redirect_stdout(buffer):
            exit_code = module.main()
        self.assertEqual(exit_code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["status"], "pass")


    def test_inventory_sort_key_is_platform_stable_posix_relative_path(self) -> None:
        from services.file_inventory import _inventory_sort_key

        sample = ROOT / "docs" / "release" / "FILE_INVENTORY.json"
        self.assertEqual(_inventory_sort_key(sample, ROOT), "docs/release/FILE_INVENTORY.json")

    def test_file_inventory_doc_and_json_exist(self) -> None:
        self.assertTrue((ROOT / "docs" / "quality" / "FILE_INVENTORY.md").exists())
        payload = json.loads((ROOT / "docs" / "release" / "FILE_INVENTORY.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("version"), "27.0.0-safe")
        self.assertGreater(payload.get("file_count", 0), 100)
        self.assertIn("package_sha256", payload)

    def test_integrity_endpoint_is_documented(self) -> None:
        api_reference = (ROOT / "docs" / "api" / "API_REFERENCE.md").read_text(encoding="utf-8")
        openapi = (ROOT / "docs" / "api" / "openapi.yaml").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("/api/integrity", api_reference)
        self.assertIn("/api/integrity:", openapi)
        self.assertIn("/api/integrity", manifest.get("api_endpoints", []))


class V19IntegrityRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            import app  # noqa: F401
        except Exception as exc:  # pragma: no cover - dependency-free source review path
            raise unittest.SkipTest(f"runtime dependencies are not installed: {exc}")

    def test_integrity_endpoint_reports_pass(self) -> None:
        from app import IPv6SentinelApp

        temp_dir = Path(tempfile.mkdtemp(prefix="ipv6_sentinel_v19_"))
        with patch.dict(os.environ, {"IPV6_SENTINEL_DATA_DIR": str(temp_dir)}):
            runtime_app = IPv6SentinelApp()
            try:
                client = runtime_app.app.test_client()
                response = client.get("/api/integrity")
                self.assertEqual(response.status_code, 200)
                payload = response.get_json()
                self.assertEqual(payload.get("status"), "pass")
                self.assertEqual(payload.get("version"), "27.0.0-safe")
            finally:
                runtime_app.shutdown()
                shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
