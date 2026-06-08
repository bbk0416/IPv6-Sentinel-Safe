from __future__ import annotations

import json
import os
import shutil
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from services.api_contract import extract_flask_api_routes, extract_openapi_routes, run_api_contract_check

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


class V13ApiContractPackagingTests(unittest.TestCase):
    def test_api_contract_script_outputs_pass_json(self) -> None:
        completed = run_command(
            [sys.executable, str(ROOT / "scripts" / "check_api_contract.py")],
            cwd=str(ROOT),
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["summary"]["flask_route_count"], 20)
        self.assertTrue(any(route["path"] == "/api/contract" for route in payload["routes"]))

    def test_api_contract_service_compares_source_docs_and_manifest(self) -> None:
        payload = run_api_contract_check(app_root=ROOT)
        self.assertEqual(payload["status"], "pass")
        check_names = {check["name"] for check in payload["checks"]}
        self.assertIn("flask_routes_documented_in_openapi", check_names)
        self.assertIn("manifest_api_paths_match_flask_routes", check_names)
        self.assertIn("api_reference_mentions_all_flask_paths", check_names)

    def test_openapi_and_flask_route_sets_match(self) -> None:
        flask_routes = extract_flask_api_routes((ROOT / "app.py").read_text(encoding="utf-8"))
        openapi_routes = extract_openapi_routes((ROOT / "docs" / "api" / "openapi.yaml").read_text(encoding="utf-8"))
        self.assertEqual(flask_routes, openapi_routes)

    def test_contract_is_part_of_release_audit_and_validation(self) -> None:
        for path in [
            "README.md",
            "docs/api/API_REFERENCE.md",
            "docs/api/openapi.yaml",
            "project_manifest.json",
            "scripts/validate_project.py",
            "docs/quality/API_CONTRACT.md",
        ]:
            with self.subTest(path=path):
                self.assertIn("api/contract", (ROOT / path).read_text(encoding="utf-8"))


@unittest.skipIf(IPv6SentinelApp is None, f"runtime dependencies are not installed: {IMPORT_ERROR}")
class V13ApiContractRuntimeTests(unittest.TestCase):
    def test_contract_endpoint_reports_pass(self) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="ipv6_sentinel_v13_"))
        with patch.dict(os.environ, {"IPV6_SENTINEL_DATA_DIR": str(temp_dir)}):
            app = IPv6SentinelApp()
            try:
                client = app.app.test_client()
                response = client.get("/api/contract")
                self.assertEqual(response.status_code, 200)
                payload = response.get_json()
                self.assertEqual(payload["status"], "pass")
            finally:
                app.shutdown()
                shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
