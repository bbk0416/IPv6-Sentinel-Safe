from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from services.preflight import run_preflight_checks

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
from process_helpers import run_command


class V12ValidationTests(unittest.TestCase):
    def test_requirements_check_outputs_pass_json(self) -> None:
        completed = run_command(
            [sys.executable, str(ROOT / "scripts" / "check_requirements.py")],
            cwd=str(ROOT),
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["blocked_absent"])
        self.assertIn("flask", payload["packages"])

    def test_source_package_preflight_treats_missing_runtime_deps_as_warning(self) -> None:
        with patch("services.preflight._module_available", return_value=False):
            payload = run_preflight_checks(
                app_root=ROOT,
                app_version="27.0.0-safe",
                safe_mode=True,
                simulation_mode=True,
                real_packet_flags={"capture": False, "send": False, "scan": False},
                host="127.0.0.1",
                port=5000,
                auth_enabled=False,
                auth_password_set=False,
                cors_origins=["http://127.0.0.1:5000"],
                dependency_severity="warning",
                profile="source_package",
            )
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["profile"], "source_package")
        dependency_check = next(check for check in payload["checks"] if check["name"] == "runtime_dependencies_available")
        self.assertFalse(dependency_check["ok"])
        self.assertEqual(dependency_check["severity"], "warning")
        self.assertEqual(payload["summary"]["warnings"], 1)

    def test_strict_preflight_treats_missing_runtime_deps_as_error(self) -> None:
        with patch("services.preflight._module_available", return_value=False):
            payload = run_preflight_checks(
                app_root=ROOT,
                app_version="27.0.0-safe",
                safe_mode=True,
                simulation_mode=True,
                real_packet_flags={"capture": False, "send": False, "scan": False},
                host="127.0.0.1",
                port=5000,
                auth_enabled=False,
                auth_password_set=False,
                cors_origins=["http://127.0.0.1:5000"],
                dependency_severity="error",
                profile="runtime",
            )
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["profile"], "runtime")

    def test_install_check_is_documented(self) -> None:
        for path in ["README.md", "docs/operations/INSTALL_CHECK.md", "scripts/validate_project.py"]:
            with self.subTest(path=path):
                self.assertIn("check_requirements", (ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
