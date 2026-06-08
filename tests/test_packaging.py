from __future__ import annotations

import unittest
from pathlib import Path
import contextlib
import io

ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_release_files_exist(self) -> None:
        required = [
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore",
            "pyproject.toml",
            "Makefile",
            ".github/workflows/ci.yml",
            "scripts/smoke_check.py",
            "scripts/validate_project.py",
            "DEPLOYMENT.md",
            "PORTFOLIO_SUMMARY.md",
            "docs/assets/dashboard-preview.svg",
            "docs/assets/dashboard-preview.png",
            "docs/api/API_REFERENCE.md",
            "docs/api/openapi.yaml",
            "docs/demo/DEMO_SCRIPT.md",
            "docs/demo/QUICK_START_CHECKLIST.md",
            "project_manifest.json",
            "docs/review/FINAL_REVIEW_CHECKLIST.md",
            "docs/security/THREAT_MODEL.md",
            "docs/release/RELEASE_PACKAGE_MANIFEST.md",
            "docs/demo/PREVIEW.html",
            "scripts/build_release.py",
            "scripts/generate_project_report.py",
            "LICENSE",
            "CONTRIBUTING.md",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists(), path)

    def test_docker_compose_uses_auth_when_exposing_container(self) -> None:
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("IPV6_SENTINEL_WEB_AUTH_ENABLED", compose)
        self.assertIn("IPV6_SENTINEL_PASSWORD", compose)
        self.assertIn("5000:5000", compose)

    def test_ci_uses_clean_validation_command(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("python scripts/run_clean_validation.py", workflow)
        self.assertNotIn("python scripts/validate_project.py", workflow)
        self.assertIn("docker build", workflow)

    def test_pyproject_declares_safe_name(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('name = "ipv6-sentinel-safe"', pyproject)
        self.assertIn('requires-python = ">=3.10"', pyproject)

    def test_readme_documents_ready_endpoint(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("/api/ready", readme)
        self.assertIn("/api/demo/scenario", readme)
        self.assertIn("docker compose up --build", readme)

    def test_project_manifest_declares_simulation_only(self) -> None:
        import json
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "27.0.0-safe")
        self.assertTrue(manifest["safe_mode"])
        self.assertFalse(manifest["real_packet_send_enabled"])
        self.assertFalse(manifest["real_network_scan_enabled"])

    def test_api_reference_documents_demo_endpoint(self) -> None:
        api_reference = (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8")
        openapi = (ROOT / "docs/api/openapi.yaml").read_text(encoding="utf-8")
        self.assertIn("/api/demo/scenario", api_reference)
        self.assertIn("/api/demo/scenario", openapi)


class LegacyPackagingTests(unittest.TestCase):
    def test_v6_docs_and_report_endpoint_are_documented(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        api_reference = (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8")
        self.assertIn("/api/report.json", readme)
        self.assertIn("/api/report.json", api_reference)
        self.assertIn("Threat Model", (ROOT / "docs/security/THREAT_MODEL.md").read_text(encoding="utf-8"))

    def test_release_builder_is_sanitized(self) -> None:
        builder = (ROOT / "scripts/build_release.py").read_text(encoding="utf-8")
        self.assertIn("EXCLUDED_PARTS", builder)
        for token in [".venv", "__pycache__", "logs", "data"]:
            self.assertIn(token, builder)


class OfflineFallbackTests(unittest.TestCase):
    def test_v13_documents_rest_fallback(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        api_reference = (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8")
        self.assertIn("REST fallback", readme)
        self.assertIn("/api/monitoring/start", api_reference)
        self.assertIn("/api/assets/generate", api_reference)

    def test_preview_png_exists(self) -> None:
        self.assertTrue((ROOT / "docs/assets/dashboard-preview.png").exists())


class ServicesPackagingTests(unittest.TestCase):
    def test_services_layer_and_honest_docs_exist(self) -> None:
        for path in [
            "services/state.py",
            "services/simulation_catalog.py",
            "services/settings_store.py",
            "services/exporters.py",
            "services/diagnostics.py",
            "docs/architecture/ARCHITECTURE.md",
            "docs/review/HONEST_LIMITATIONS.md",
            "scripts/check_frontend_bindings.py",
        ]:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists(), path)

    def test_docker_compose_requires_password_without_weak_default(self) -> None:
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("IPV6_SENTINEL_PASSWORD:?Set IPV6_SENTINEL_PASSWORD", compose)
        self.assertNotIn("change-this-password", compose)

    def test_frontend_binding_script_passes(self) -> None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("check_frontend_bindings", ROOT / "scripts" / "check_frontend_bindings.py")
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exit_code = module.main()
        self.assertEqual(exit_code, 0)
        self.assertIn("[OK]", buffer.getvalue())


class DiagnosticsPackagingTests(unittest.TestCase):
    def test_diagnostics_endpoint_is_documented(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        api_reference = (ROOT / "docs/api/API_REFERENCE.md").read_text(encoding="utf-8")
        openapi = (ROOT / "docs/api/openapi.yaml").read_text(encoding="utf-8")
        manifest = (ROOT / "project_manifest.json").read_text(encoding="utf-8")
        self.assertIn("/api/diagnostics", readme)
        self.assertIn("/api/diagnostics", api_reference)
        self.assertIn("/api/diagnostics", openapi)
        self.assertIn("/api/diagnostics", manifest)


if __name__ == "__main__":
    unittest.main()
