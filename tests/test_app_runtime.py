from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("IPV6_SENTINEL_LOG_CONSOLE_ENABLED", "0")
os.environ.setdefault("IPV6_SENTINEL_LOG_FILE_ENABLED", "0")

try:
    from app import IPv6SentinelApp
    from utils.performance_monitor import PerformanceMonitor
except ModuleNotFoundError as exc:  # Allows static tests before runtime dependencies are installed.
    IPv6SentinelApp = None  # type: ignore[assignment]
    PerformanceMonitor = None  # type: ignore[assignment]
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


@unittest.skipIf(IPv6SentinelApp is None, f"runtime dependencies are not installed: {IMPORT_ERROR}")
class AppRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ipv6_sentinel_test_"))
        self.env_patch = patch.dict(os.environ, {"IPV6_SENTINEL_DATA_DIR": str(self.temp_dir)})
        self.env_patch.start()
        self.app = IPv6SentinelApp()
        self.client = self.app.app.test_client()

    def tearDown(self) -> None:
        self.app.shutdown()
        self.env_patch.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_core_http_routes_return_success(self) -> None:
        for path in [
            "/",
            "/api/health",
            "/api/info",
            "/api/ready",
            "/api/stats",
            "/api/assets",
            "/api/logs",
            "/api/logs.csv",
            "/api/snapshot.json",
            "/api/report.json",
            "/api/diagnostics",
            "/api/preflight",
            "/api/quality",
            "/api/contract",
            "/api/schema",
            "/api/release",
            "/api/artifact",
            "/api/integrity",
            "/api/manifest",
            "/api/publication",
            "/api/gates",
            "/api/capabilities",
            "/api/reviewer",
            "/api/settings",
        ]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_settings_are_clamped_and_saved(self) -> None:
        response = self.client.post(
            "/api/settings",
            json={
                "interface": "A" * 200,
                "simulation_speed": 999,
                "event_retention": -1,
                "policy_response_enabled": False,
                "threat_detection": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["simulation_speed"], 10)
        self.assertEqual(payload["event_retention"], 50)
        self.assertLessEqual(len(payload["interface"]), 80)
        self.assertFalse(payload["policy_response_enabled"])
        self.assertTrue(self.app.ui_settings_path.exists())

    def test_reset_and_sample_inventory_are_safe_local_operations(self) -> None:
        self.app._generate_sample_asset_inventory()
        self.assertEqual(len(self.app._asset_list()), 5)
        response = self.client.post("/api/reset")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "reset")
        self.assertEqual(payload["assets"], [])
        self.assertEqual(payload["stats"]["total_events"], 0)

    def test_missing_network_counters_do_not_crash(self) -> None:
        with patch("psutil.net_io_counters", return_value=None):
            monitor = PerformanceMonitor()
            snapshot = monitor.snapshot()
            stats = self.app._stats_snapshot()
        self.assertEqual(snapshot["network_throughput_mbps"], 0.0)
        self.assertEqual(stats["network_total_mb"], 0.0)

    def test_demo_scenario_endpoint_seeds_safe_data(self) -> None:
        response = self.client.post("/api/demo/scenario")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "seeded")
        self.assertEqual(payload["scenario"], "portfolio_demo")
        self.assertEqual(len(payload["assets"]), 5)
        self.assertGreaterEqual(payload["stats"]["total_events"], 8)
        self.assertTrue(any(entry["event_type"] == "demo_scenario" for entry in payload["logs"]))

    def test_info_snapshot_and_security_headers_are_present(self) -> None:
        info = self.client.get("/api/info")
        self.assertEqual(info.status_code, 200)
        self.assertTrue(info.get_json()["safe_mode"])
        self.assertEqual(info.get_json()["real_packet_send_enabled"], False)

        ready = self.client.get("/api/ready")
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(ready.get_json()["status"], "ready")

        snapshot = self.client.get("/api/snapshot.json")
        self.assertEqual(snapshot.status_code, 200)
        self.assertIn("attachment", snapshot.headers.get("Content-Disposition", ""))
        self.assertEqual(snapshot.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(snapshot.headers.get("X-Frame-Options"), "DENY")

    def test_rest_fallback_control_endpoints_work(self) -> None:
        start = self.client.post("/api/monitoring/start")
        self.assertEqual(start.status_code, 200)
        self.assertEqual(start.get_json()["status"], "started")

        assets = self.client.post("/api/assets/generate")
        self.assertEqual(assets.status_code, 200)
        self.assertGreaterEqual(len(assets.get_json()["assets"]), 5)

        speed = self.client.post("/api/simulation/speed", json={"speed": 99})
        self.assertEqual(speed.status_code, 200)
        self.assertEqual(speed.get_json()["speed"], 10)

        clear = self.client.post("/api/logs/clear")
        self.assertEqual(clear.status_code, 200)
        self.assertEqual(clear.get_json()["status"], "cleared")

        stop = self.client.post("/api/monitoring/stop")
        self.assertEqual(stop.status_code, 200)
        self.assertEqual(stop.get_json()["status"], "stopped")


    def test_diagnostics_endpoint_reports_safe_state(self) -> None:
        response = self.client.get("/api/diagnostics")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["mode"], "safe_simulation")
        self.assertEqual(payload["version"], "27.0.0-safe")
        check_names = {check["name"] for check in payload["checks"]}
        self.assertIn("real_packet_features_disabled", check_names)
        self.assertIn("no_blocked_network_imports", check_names)


    def test_quality_endpoint_reports_pass(self) -> None:
        response = self.client.get("/api/quality")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")
        self.assertTrue(any(check["name"] == "version_declarations_match" for check in payload["checks"]))


    def test_release_endpoint_reports_safe_release_identity(self) -> None:
        response = self.client.get("/api/release")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")
        check_names = {check["name"] for check in payload["checks"]}
        self.assertIn("settings_version_matches_current_release", check_names)
        self.assertIn("pyproject_version_matches_normalized_package_version", check_names)

    def test_portfolio_report_export_is_safe(self) -> None:
        response = self.client.get("/api/report.json")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["safety"]["ready"])
        self.assertFalse(payload["safety"]["real_packet_send_enabled"])
        self.assertEqual(payload["project"]["version"], "27.0.0-safe")

    def test_auth_can_be_enabled_with_basic_auth(self) -> None:
        with patch("app.WEB_AUTH_ENABLED", True), patch("app.WEB_AUTH_USERNAME", "admin"), patch("app.WEB_AUTH_PASSWORD", "secret"):
            protected = IPv6SentinelApp()
            client = protected.app.test_client()
            unauthorized = client.get("/api/health")
            self.assertEqual(unauthorized.status_code, 401)
            authorized = client.get("/api/health", headers={"Authorization": "Basic YWRtaW46c2VjcmV0"})
            self.assertEqual(authorized.status_code, 200)
            protected.shutdown()

    def test_remote_bind_without_auth_fails_closed(self) -> None:
        with patch("app.FLASK_HOST", "0.0.0.0"), patch("app.WEB_AUTH_ENABLED", False), patch("app.ALLOW_REMOTE_BIND_WITHOUT_AUTH", False):
            with self.assertRaises(RuntimeError):
                IPv6SentinelApp()


if __name__ == "__main__":
    unittest.main()
