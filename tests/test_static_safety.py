from __future__ import annotations

import ast
import re
import unittest
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def _project_py_files() -> list[Path]:
    files: list[Path] = []
    skip_parts = {'.venv', '.testvenv', 'venv', 'env', 'node_modules', '__pycache__'}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [name for name in dirnames if name not in skip_parts]
        current = Path(dirpath)
        for filename in filenames:
            if filename.endswith('.py'):
                files.append(current / filename)
    return sorted(files)


def _project_text_files() -> list[Path]:
    """Return active UI/server text paths for legacy UI-token checks."""
    suffixes = {'.py', '.js', '.html', '.css'}
    roots = [ROOT / 'static', ROOT / 'templates']
    files: list[Path] = [ROOT / 'app.py']
    skip_parts = {'.venv', '.testvenv', 'venv', 'env', 'node_modules', '__pycache__'}
    for base in roots:
        if not base.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [name for name in dirnames if name not in skip_parts]
            current = Path(dirpath)
            for filename in filenames:
                path = current / filename
                if path.suffix.lower() in suffixes:
                    files.append(path)
    return sorted(path for path in files if path.exists())



PY_FILES = _project_py_files()
TEXT_FILES = _project_text_files()



class StaticSafetyTests(unittest.TestCase):
    def test_python_files_parse(self) -> None:
        for path in PY_FILES:
            with self.subTest(path=path):
                ast.parse(path.read_text(encoding='utf-8'))

    def test_no_high_risk_network_libraries_imported(self) -> None:
        blocked_imports = {'scapy', 'mitmproxy', 'wmi'}
        for path in PY_FILES:
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported = {alias.name.split('.')[0] for alias in node.names}
                    self.assertFalse(imported & blocked_imports, f'{path} imports {imported & blocked_imports}')
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported_root = node.module.split('.')[0]
                    self.assertNotIn(imported_root, blocked_imports, f'{path} imports {imported_root}')

    def test_active_ui_uses_monitoring_names(self) -> None:
        forbidden_tokens = ['start_attack', 'stop_attack', 'attack_status', 'attack_log', 'set_attack_intensity', 'dhcp_spoof', 'dns_spoof']
        for path in TEXT_FILES:
            text = path.read_text(encoding='utf-8')
            for token in forbidden_tokens:
                with self.subTest(path=path, token=token):
                    self.assertNotIn(token, text)

    def test_server_defaults_to_localhost(self) -> None:
        settings = (ROOT / 'settings.py').read_text(encoding='utf-8')
        self.assertIn('127.0.0.1', settings)
        self.assertNotIn('FLASK_HOST = "0.0.0.0"', settings)


    def test_dashboard_has_rest_fallback_for_cdn_failure(self) -> None:
        dashboard = (ROOT / 'static' / 'dashboard.js').read_text(encoding='utf-8')
        app_text = (ROOT / 'app.py').read_text(encoding='utf-8')
        self.assertIn('enterRestFallbackMode', dashboard)
        self.assertIn('/api/monitoring/start', app_text)
        self.assertIn('/api/assets/generate', app_text)

    def test_no_wildcard_cors_default(self) -> None:
        settings = (ROOT / 'settings.py').read_text(encoding='utf-8')
        self.assertNotIn('SOCKETIO_CORS_ALLOWED_ORIGINS = "*"', settings)
        self.assertIn('IPV6_SENTINEL_CORS', settings)


    def test_config_logger_masks_local_network_identifiers(self) -> None:
        source = (ROOT / "models" / "config_manager.py").read_text(encoding="utf-8")
        self.assertIn("_mask_ipv4", source)
        self.assertIn("_mask_ipv6", source)
        self.assertIn("_mask_mac", source)
        self.assertIn("self._mask_ipv4(self.v4addr)", source)
        self.assertIn("self._mask_ipv6(self.v6addr)", source)
        self.assertIn("self._mask_mac(self.macaddr)", source)
        self.assertNotIn("self.v4addr or \"없음\"", source)
        self.assertNotIn("self.macaddr or \"없음\"", source)

    def test_test_modules_have_unique_class_names(self) -> None:
        import collections
        for path in sorted((ROOT / 'tests').glob('test_*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            class_names = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
            duplicates = sorted(name for name, count in collections.Counter(class_names).items() if count > 1)
            with self.subTest(path=path.name):
                self.assertEqual(duplicates, [])

    def test_no_module_level_test_functions_for_unittest_discovery(self) -> None:
        for path in sorted((ROOT / 'tests').glob('test_*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            module_level_tests = [node.name for node in tree.body if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
            with self.subTest(path=path.name):
                self.assertEqual(module_level_tests, [])

    def test_unittest_main_blocks_are_last(self) -> None:
        for path in sorted((ROOT / 'tests').glob('test_*.py')):
            lines = path.read_text(encoding='utf-8').splitlines()
            main_lines = [idx + 1 for idx, line in enumerate(lines) if line.strip().startswith('if __name__')]
            if not main_lines:
                continue
            tree = ast.parse('\n'.join(lines))
            last_class_line = max((node.lineno for node in tree.body if isinstance(node, ast.ClassDef)), default=0)
            with self.subTest(path=path.name):
                self.assertTrue(all(line > last_class_line for line in main_lines), f'__main__ block appears before class definitions: {main_lines}')



    def test_readme_current_feature_language_uses_current_release(self) -> None:
        """Keep active quick-start/current-feature docs from drifting to old release labels."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        quick_start = (ROOT / "docs" / "demo" / "QUICK_START_CHECKLIST.md").read_text(encoding="utf-8")

        stale_current_phrases = [
            "v18에서도",
            "v18 대시보드",
            "## v18 검증 기준",
            "v18 automatically switches",
        ]
        joined = readme + "\n" + quick_start
        for phrase in stale_current_phrases:
            self.assertNotIn(phrase, joined)

        self.assertIn("현재 v27 패키지", readme)
        self.assertIn("현재 v27 대시보드", readme)
        self.assertIn("## v27 검증 기준", readme)
        self.assertIn("current v27 dashboard", quick_start)

    def test_makefile_targets_are_unique_and_phony_complete(self) -> None:
        """Keep reviewer-facing Make targets deterministic and non-shadowed."""
        import re
        import collections

        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        targets = []
        for line in makefile.splitlines():
            if not line or line.startswith(("\t", " ", ".")):
                continue
            if ":" in line and ":=" not in line and "?=" not in line:
                targets.append(line.split(":", 1)[0].strip())
        duplicates = sorted(name for name, count in collections.Counter(targets).items() if count > 1)
        self.assertEqual(duplicates, [])

        match = re.search(r"^\.PHONY:\s*(.*)$", makefile, re.MULTILINE)
        self.assertIsNotNone(match, "Makefile should declare .PHONY targets")
        phony = set(match.group(1).split())
        self.assertEqual(sorted(set(targets) - phony), [])
        self.assertEqual(sorted(phony - set(targets)), [])

    def test_release_note_lead_lines_match_file_version(self) -> None:
        """Avoid review-confusing release-note identity drift."""
        for path in sorted(ROOT.glob('RELEASE_NOTES_v*.md'), key=lambda item: int(item.stem.split('_v')[-1])):
            expected = path.stem.split('_v')[-1]
            lines = [line.strip() for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
            lead_lines = [line for line in lines if not line.startswith('#')]
            self.assertTrue(lead_lines, f'{path.name} should contain a prose lead line')
            lead = lead_lines[0]
            with self.subTest(path=path.name):
                self.assertIn(f'v{expected}', lead)
                wrong_versions = [f'v{num}' for num in range(10, 28) if str(num) != expected and f'v{num}' in lead]
                self.assertEqual(wrong_versions, [])


    def test_active_handoff_docs_do_not_use_legacy_version_headings(self) -> None:
        """Current handoff docs should not present old gate versions as active headings."""
        import re

        active_docs = [
            ROOT / "README.md",
            ROOT / "docs" / "demo" / "QUICK_START_CHECKLIST.md",
            ROOT / "docs" / "operations" / "PREFLIGHT.md",
            ROOT / "docs" / "quality" / "QUALITY_GATE.md",
            ROOT / "docs" / "release" / "RELEASE_PACKAGE_MANIFEST.md",
            ROOT / "docs" / "review" / "FINAL_REVIEW_CHECKLIST.md",
        ]
        legacy_heading = re.compile(r"^#{1,6}\s+v(?:[3-9]|1[0-9]|2[0-6])(?:\.|\b)", re.IGNORECASE)
        for path in active_docs:
            lines = path.read_text(encoding="utf-8").splitlines()
            offenders = [line for line in lines if legacy_heading.match(line.strip())]
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertEqual(offenders, [])


    def test_final_handoff_docs_match_compact_default_behavior(self) -> None:
        """Keep final handoff docs aligned with the compact default command."""
        active_docs = [
            ROOT / "docs" / "quality" / "FINAL_HANDOFF.md",
            ROOT / "README.md",
            ROOT / "docs" / "review" / "FINAL_REVIEW_CHECKLIST.md",
            ROOT / "docs" / "release" / "RELEASE_PACKAGE_MANIFEST.md",
        ]
        for path in active_docs:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIn("run_clean_validation.py", text)
                self.assertIn("--plan", text)
                self.assertNotIn("refreshes file inventory, builds a temporary sanitized ZIP, validates the ZIP, and cleans again", text)

        script = (ROOT / "scripts" / "final_handoff_check.py").read_text(encoding="utf-8")
        self.assertIn("compact", script)
        self.assertIn("focused unittest handoff subset", script)
        self.assertNotIn("Also run unittest discovery as part of the handoff gate", script)

    def test_project_version_is_current_safe(self) -> None:
        settings = (ROOT / 'settings.py').read_text(encoding='utf-8')
        pyproject = (ROOT / 'pyproject.toml').read_text(encoding='utf-8')
        self.assertIn('APP_VERSION = "27.0.0-safe"', settings)
        self.assertIn('version = "27.0.0"', pyproject)

    def test_logger_supports_quiet_test_mode(self) -> None:
        settings_text = (ROOT / 'settings.py').read_text(encoding='utf-8')
        logger_text = (ROOT / 'utils' / 'logger.py').read_text(encoding='utf-8')
        runtime_tests = (ROOT / 'tests' / 'test_app_runtime.py').read_text(encoding='utf-8')
        self.assertIn('IPV6_SENTINEL_LOG_CONSOLE_ENABLED', settings_text)
        self.assertIn('IPV6_SENTINEL_LOG_FILE_ENABLED', settings_text)
        self.assertIn('LOG_CONSOLE_ENABLED', logger_text)
        self.assertIn('LOG_FILE_ENABLED', logger_text)
        self.assertIn('IPV6_SENTINEL_LOG_FILE_ENABLED', runtime_tests)


    def test_runtime_data_dir_is_env_configurable_for_tests(self) -> None:
        app = (ROOT / 'app.py').read_text(encoding='utf-8')
        runtime_tests = (ROOT / 'tests' / 'test_app_runtime.py').read_text(encoding='utf-8')
        env_example = (ROOT / '.env.example').read_text(encoding='utf-8')
        self.assertIn('IPV6_SENTINEL_DATA_DIR', app)
        self.assertIn('IPV6_SENTINEL_DATA_DIR', runtime_tests)
        self.assertIn('IPV6_SENTINEL_DATA_DIR', env_example)
        self.assertNotIn('self.app.data_dir = self.temp_dir', runtime_tests)


    def test_no_duplicate_legacy_current_release_gate_tests(self) -> None:
        duplicate_legacy_tests = [
            "tests/test_v26_capability_boundary.py",
            "tests/test_v26_gate_registry.py",
            "tests/test_v26_publication_hygiene.py",
        ]
        present = [path for path in duplicate_legacy_tests if (ROOT / path).exists()]
        self.assertEqual(present, [], "v26-named tests should not duplicate current v27 gate tests")

    def test_runtime_tests_do_not_pass_stray_base_url_to_settings_post(self) -> None:
        runtime_tests = (ROOT / 'tests' / 'test_app_runtime.py').read_text(encoding='utf-8')
        self.assertNotIn('self.client.post(\n            "/api/settings",\n            "/api/capabilities",', runtime_tests)

    def test_active_inventory_progress_uses_simulation_vocabulary(self):
        app_source = (ROOT / "app.py").read_text(encoding="utf-8")
        dashboard_source = (ROOT / "static" / "dashboard.js").read_text(encoding="utf-8")
        css_source = (ROOT / "static" / "dashboard.css").read_text(encoding="utf-8")
        self.assertIn('"processed": index', app_source)
        self.assertNotIn('"scanned": index', app_source)
        self.assertIn('progress.processed', dashboard_source)
        self.assertNotIn('progress.scanned', dashboard_source)
        self.assertIn('@keyframes safeSweep', css_source)
        self.assertNotIn('@keyframes scan', css_source)

    def test_versioned_test_class_names_match_file_version(self) -> None:
        """Keep reviewer-facing test names aligned with their test-module version."""
        import ast
        import re

        for path in sorted((ROOT / "tests").glob("test_v*_*.py")):
            match = re.match(r"test_v(\d+)_", path.name)
            if not match:
                continue
            expected = f"V{match.group(1)}"
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_match = re.match(r"V(\d+)", node.name)
                    if class_match:
                        self.assertTrue(
                            node.name.startswith(expected),
                            f"{path.name} contains version-drifted test class {node.name}; expected prefix {expected}",
                        )

    def test_versioned_test_method_names_match_file_version(self) -> None:
        """Keep reviewer-facing versioned test method names aligned with their module."""
        import ast
        import re

        for path in sorted((ROOT / "tests").glob("test_v*_*.py")):
            match = re.match(r"test_v(\d+)_", path.name)
            if not match:
                continue
            expected_version = match.group(1)
            expected = f"test_v{expected_version}_"
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    embedded_versions = re.findall(r"(?<![A-Za-z0-9])v(\d+)(?![A-Za-z0-9])", node.name)
                    wrong_versions = [version for version in embedded_versions if version != expected_version]
                    self.assertEqual(
                        wrong_versions,
                        [],
                        f"{path.name} contains version-drifted test method {node.name}; expected only v{expected_version}",
                    )
                    method_match = re.match(r"test_v(\d+)_", node.name)
                    if method_match:
                        self.assertTrue(
                            node.name.startswith(expected),
                            f"{path.name} contains version-drifted test method {node.name}; expected prefix {expected}",
                        )



    def test_versioned_tests_reference_matching_release_notes(self) -> None:
        """Keep versioned test modules from pointing at unrelated historical release notes."""
        import re

        for path in sorted((ROOT / "tests").glob("test_v*_*.py")):
            match = re.match(r"test_v(\d+)_", path.name)
            if not match:
                continue
            expected_version = match.group(1)
            text = path.read_text(encoding="utf-8")
            referenced = sorted(set(re.findall(r"RELEASE_NOTES_v(\d+)\.md", text)), key=int)
            wrong_versions = [version for version in referenced if version not in {expected_version, "27"}]
            self.assertEqual(
                wrong_versions,
                [],
                f"{path.name} references release notes outside v{expected_version}/current v27: {wrong_versions}",
            )

    def test_current_release_id_docs_do_not_prefix_semver_with_v(self) -> None:
        """Keep the safe release ID visually consistent with app/API payloads."""
        docs = [
            ROOT / "README.md",
            ROOT / "PROJECT_COMPLETION_REPORT.md",
            ROOT / "docs" / "operations" / "INSTALL_CHECK.md",
            ROOT / "docs" / "operations" / "PREFLIGHT.md",
            ROOT / "docs" / "quality" / "SCHEMA_CONTRACT.md",
            ROOT / "docs" / "quality" / "PUBLICATION_HYGIENE.md",
            ROOT / "docs" / "release" / "RELEASE_PACKAGE_MANIFEST.md",
            ROOT / "docs" / "review" / "FINAL_REVIEW_CHECKLIST.md",
            ROOT / "RELEASE_NOTES_v27.md",
        ]
        prefixed_release_id = "v" + "27.0.0-safe"
        for path in docs:
            self.assertNotIn(
                prefixed_release_id,
                path.read_text(encoding="utf-8"),
                f"{path.relative_to(ROOT)} should use the safe release ID 27.0.0-safe without a v prefix",
            )

    def test_release_docs_distinguish_safe_release_id_from_package_version(self) -> None:
        """Avoid claiming pyproject uses the hyphenated safe release ID."""
        docs = [
            ROOT / "README.md",
            ROOT / "docs" / "quality" / "RELEASE_MATRIX.md",
            ROOT / "docs" / "quality" / "QUALITY_GATE.md",
            ROOT / "docs" / "api" / "API_REFERENCE.md",
            ROOT / "docs" / "release" / "RELEASE_PACKAGE_MANIFEST.md",
            ROOT / "docs" / "review" / "FINAL_REVIEW_CHECKLIST.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in docs)
        self.assertIn("normalized PEP 440 package version", combined)
        self.assertIn("27.0.0", combined)
        forbidden_claims = [
            "same release version",
            "one version in the UI, another in `pyproject.toml`",
            "current release version appears consistently in",
            "Version declarations match across settings, pyproject, OpenAPI, and manifest",
        ]
        for claim in forbidden_claims:
            self.assertNotIn(claim, combined)


    def test_release_packaging_blocks_nested_zip_files(self):
        build_release = (ROOT / "scripts" / "build_release.py").read_text(encoding="utf-8")
        check_release_zip = (ROOT / "scripts" / "check_release_zip.py").read_text(encoding="utf-8")
        release_artifact = (ROOT / "services" / "release_artifact.py").read_text(encoding="utf-8")
        self.assertIn("'.zip'", build_release)
        self.assertIn('".zip"', check_release_zip)
        self.assertIn('".zip"', release_artifact)

    def test_test_modules_have_unique_test_method_names(self) -> None:
        """Prevent unittest methods from silently shadowing earlier definitions."""
        duplicates = []
        for path in sorted((ROOT / "tests").glob("test_*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    methods = [
                        item.name
                        for item in node.body
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test_")
                    ]
                    repeated = sorted({name for name in methods if methods.count(name) > 1})
                    for name in repeated:
                        duplicates.append(f"{path.relative_to(ROOT)}::{node.name}.{name}")
        self.assertEqual(duplicates, [])

    def test_make_test_and_validate_use_clean_validation_runner(self):
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("scripts/run_clean_validation.py", makefile)
        self.assertIn("scripts/run_full_tests.py", makefile)
        self.assertRegex(makefile, r"(?m)^test:\n(?:\t.*\n)*\t\$\(PYTHON\) scripts/run_clean_validation\.py")
        self.assertRegex(makefile, r"(?m)^validate:\n\t\$\(PYTHON\) scripts/run_clean_validation\.py")
        self.assertRegex(makefile, r"(?m)^full-test:\n\t\$\(PYTHON\) scripts/run_full_tests\.py")
        self.assertRegex(makefile, r"(?m)^project-validate:\n\t\$\(PYTHON\) scripts/validate_project\.py")
        self.assertNotRegex(makefile, r"python\s+-m\s+unittest\s+discover\s+-s\s+tests")

    def test_optional_full_test_runner_uses_subprocess_isolation(self):
        runner = (ROOT / "scripts" / "run_full_tests.py").read_text(encoding="utf-8")
        self.assertIn("subprocess.Popen", runner)
        self.assertIn("TemporaryDirectory", runner)
        self.assertIn("unittest", runner)
        self.assertIn("discover", runner)
        self.assertIn("IPV6_SENTINEL_DATA_DIR", runner)
        self.assertIn("PYTHONDONTWRITEBYTECODE", runner)
        self.assertIn("isolated_subprocess_kwargs", runner)
        self.assertIn("terminate_process_tree", runner)
        self.assertIn("running full unittest discovery", runner)
        self.assertIn("os._exit", runner)
        self.assertIn("_wait_for_process", runner)
        self.assertIn("proc.poll()", runner)
        self.assertIn("time.monotonic()", runner)
        self.assertIn("COMPLETION_SETTLE_SECONDS", runner)
        self.assertIn("COMPLETION_CHECK_AFTER_SECONDS", runner)
        self.assertIn("_discovery_completion_state", runner)
        self.assertNotIn("proc.wait(timeout=timeout)", runner)

    def test_clean_release_artifacts_removes_stray_zip_files(self):
        cleaner = (ROOT / "scripts" / "clean_release_artifacts.py").read_text(encoding="utf-8")
        self.assertIn('".zip"', cleaner)
        self.assertIn("stray nested ZIP", cleaner)

    def test_current_docs_prefer_clean_validation_over_raw_discover(self):
        current_docs = [
            "README.md",
            "DEPLOYMENT.md",
            "docs/operations/INSTALL_CHECK.md",
            "docs/demo/QUICK_START_CHECKLIST.md",
            "docs/review/FINAL_REVIEW_CHECKLIST.md",
            "VALIDATION_REPORT.md",
            "RELEASE_NOTES_v27.md",
        ]
        raw_discover = re.compile(
            r"(?:PYTHONPATH=\S+\s+)?(?:PYTHONDONTWRITEBYTECODE=1\s+)?"
            r"python\s+-m\s+unittest\s+discover\s+-s\s+tests(?:\s+-[A-Za-z]+)?"
        )
        stale_primary_command = re.compile(r"python\s+scripts/validate_project\.py\s*(?:`|$)")
        for relative in current_docs:
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("scripts/run_clean_validation.py", text, relative)
            self.assertIsNone(raw_discover.search(text), relative)
            if relative in {
                "README.md",
                "DEPLOYMENT.md",
                "docs/operations/INSTALL_CHECK.md",
                "docs/demo/QUICK_START_CHECKLIST.md",
                "docs/review/FINAL_REVIEW_CHECKLIST.md",
            }:
                self.assertIsNone(stale_primary_command.search(text), relative)


    def test_ci_uses_canonical_clean_validation_command(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("python scripts/run_clean_validation.py", workflow)
        self.assertNotIn("python scripts/validate_project.py", workflow)

    def test_current_runtime_examples_do_not_reference_legacy_release_labels(self):
        """Keep active environment/deployment examples from suggesting old release phases."""
        current_files = [
            ".env.example",
            "Dockerfile",
            "docker-compose.yml",
            "README.md",
            "DEPLOYMENT.md",
            "docs/operations/INSTALL_CHECK.md",
            "docs/operations/PREFLIGHT.md",
        ]
        legacy_release_label = re.compile(r"(?i)\bv(?:[3-9]|1[0-9]|2[0-6])\b")
        offenders = []
        for relative in current_files:
            for lineno, line in enumerate((ROOT / relative).read_text(encoding="utf-8").splitlines(), start=1):
                if "RELEASE_NOTES_" in line or "test_v" in line:
                    continue
                if legacy_release_label.search(line):
                    offenders.append(f"{relative}:{lineno}:{line.strip()}")
        self.assertEqual(offenders, [])

    def test_active_non_history_docs_do_not_use_legacy_release_labels(self):
        """Keep current handoff docs/scripts from showing old internal iteration labels."""
        active_files = [
            ROOT / "docs" / "architecture" / "ARCHITECTURE.md",
            ROOT / "scripts" / "check_schema_contract.py",
        ]
        legacy_label = re.compile(r"\bv(?:[3-9]|1[0-9]|2[0-6])\b")
        offenders = []
        for path in active_files:
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if legacy_label.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{lineno}:{line.strip()}")
        self.assertEqual(offenders, [])


    def test_policy_response_naming_does_not_imply_real_blocking(self):
        """Keep simulator policy examples from looking like real blocking controls."""
        active_paths = [
            ROOT / "app.py",
            ROOT / "services" / "schemas.py",
            ROOT / "services" / "settings_store.py",
            ROOT / "services" / "simulation_catalog.py",
            ROOT / "services" / "state.py",
            ROOT / "static" / "dashboard.js",
            ROOT / "templates" / "index.html",
            ROOT / "tests" / "test_app_runtime.py",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in active_paths)
        forbidden = [
            "policy_" + "block_simulated",
            "blocked_" + "events",
            "auto_" + "block",
            "blocked-" + "events",
            "auto-" + "block",
            "정책 " + "차단",
        ]
        for token in forbidden:
            self.assertNotIn(token, combined)
        self.assertIn("policy_response_simulated", combined)
        self.assertIn("policy_response_events", combined)
        self.assertIn("policy_response_enabled", combined)


    def test_active_cdn_fallback_docs_use_access_restriction_wording(self):
        """Keep CDN fallback docs from using generic blocked/block wording."""
        active_paths = [
            ROOT / "docs" / "architecture" / "ARCHITECTURE.md",
            ROOT / "docs" / "quality" / "ROUTE_HYGIENE.md",
            ROOT / "docs" / "review" / "FINAL_REVIEW_CHECKLIST.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in active_paths)
        forbidden = [
            "CDN access is " + "blocked",
            "CDN-" + "blocked",
            "CDN “" + "block",
        ]
        for token in forbidden:
            self.assertNotIn(token, combined)
        self.assertIn("CDN access is restricted", combined)
        self.assertIn("CDN-restricted", combined)



class ReportStaticSafetyTests(unittest.TestCase):
    def test_report_export_is_present_without_dangerous_imports(self) -> None:
        app_text = (ROOT / 'app.py').read_text(encoding='utf-8')
        self.assertIn('/api/report.json', app_text)
        self.assertIn('def _portfolio_report', app_text)
        self.assertNotIn('from scapy', app_text)


class ServiceLayerStaticSafetyTests(unittest.TestCase):
    def test_simulation_catalog_uses_documentation_addresses(self) -> None:
        catalog = (ROOT / "services" / "simulation_catalog.py").read_text(encoding="utf-8")
        self.assertIn("192.0.2.", catalog)
        self.assertIn("fe80::", catalog)
        self.assertNotIn("27.0.0.", catalog)

    def test_app_uses_services_for_catalog_and_state(self) -> None:
        app_text = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("from services.simulation_catalog import", app_text)
        self.assertIn("from services.state import MonitoringStats", app_text)
        self.assertIn("from services.settings_store import", app_text)
        self.assertIn("from services.exporters import", app_text)
        self.assertIn("from services.diagnostics import", app_text)
        self.assertNotIn("class MonitoringStats:", app_text)

    def test_diagnostics_route_exists(self) -> None:
        app_text = (ROOT / "app.py").read_text(encoding="utf-8")
        diagnostics_text = (ROOT / "services" / "diagnostics.py").read_text(encoding="utf-8")
        self.assertIn('/api/diagnostics', app_text)
        self.assertIn('runtime_diagnostics', diagnostics_text)


if __name__ == '__main__':
    unittest.main()

