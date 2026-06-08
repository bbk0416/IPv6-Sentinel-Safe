from pathlib import Path
import ast
import importlib.util
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
from process_helpers import run_command


class V23ValidationHygieneTests(unittest.TestCase):
    def test_validation_hygiene_files_exist(self):
        required = [
            "services/validation_hygiene.py",
            "scripts/check_validation_hygiene.py",
            "scripts/run_clean_validation.py",
            "services/process_control.py",
            "docs/quality/VALIDATION_HYGIENE.md",
            "RELEASE_NOTES_v27.md",
        ]
        missing = [item for item in required if not (ROOT / item).exists()]
        self.assertEqual(missing, [])


    def test_process_control_helper_is_cross_platform(self):
        text = (ROOT / "services" / "process_control.py").read_text(encoding="utf-8")
        self.assertIn('os.name == "nt"', text)
        self.assertIn("CREATE_NEW_PROCESS_GROUP", text)
        self.assertIn("start_new_session", text)
        self.assertIn("proc.terminate()", text)
        self.assertIn("proc.kill()", text)

    def test_validate_project_cleans_artifacts(self):
        text = (ROOT / "scripts/validate_project.py").read_text(encoding="utf-8")
        self.assertIn("cleanup_generated_artifacts", text)
        self.assertIn("sys.dont_write_bytecode = True", text)
        self.assertIn("finally:", text)
        self.assertIn("TemporaryDirectory", text)
        self.assertIn("isolated_subprocess_kwargs", text)
        self.assertIn("terminate_process_tree", text)

    def test_validation_hygiene_script_passes(self):
        proc = run_command(
            [sys.executable, "scripts/check_validation_hygiene.py"],
            cwd=ROOT,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")


    def test_clean_validation_runner_uses_file_backed_process_group_cleanup(self):
        text = (ROOT / "scripts/run_clean_validation.py").read_text(encoding="utf-8")
        self.assertIn("subprocess.Popen", text)
        self.assertIn("isolated_subprocess_kwargs", text)
        self.assertIn("terminate_process_tree", text)
        self.assertIn("TemporaryDirectory", text)
        self.assertIn("_direct_clean_step", text)
        self.assertIn("_direct_validation_hygiene_step", text)
        self.assertIn("os._exit", text)
        self.assertNotIn("capture_output=True", text)


    def test_validate_project_unittest_runner_uses_file_backed_cleanup(self):
        text = (ROOT / "scripts/validate_project.py").read_text(encoding="utf-8")
        runner_block = text.split("def _run_unittest_module", 1)[1].split("def run_unittests", 1)[0]
        self.assertIn("subprocess.Popen", runner_block)
        self.assertIn("isolated_subprocess_kwargs", runner_block)
        self.assertIn("terminate_process_tree", runner_block)
        self.assertIn("TemporaryDirectory", runner_block)
        self.assertIn("proc.wait(timeout=timeout_seconds)", runner_block)
        self.assertNotIn("stdout=subprocess.PIPE", runner_block)
        self.assertNotIn("stderr=subprocess.PIPE", runner_block)
        self.assertNotIn("communicate(timeout=timeout_seconds)", runner_block)


    def test_validate_project_avoids_pipe_capture_for_internal_script_checks(self):
        text = (ROOT / "scripts/validate_project.py").read_text(encoding="utf-8")
        self.assertNotIn("capture_output=True", text)
        self.assertNotIn("stdout=subprocess.PIPE", text)
        self.assertNotIn("stderr=subprocess.PIPE", text)
        self.assertNotIn("communicate(timeout=timeout_seconds)", text)


    def test_full_test_runner_uses_polling_process_group_cleanup(self):
        text = (ROOT / "scripts/run_full_tests.py").read_text(encoding="utf-8")
        self.assertIn("def _wait_for_process", text)
        self.assertIn("import contextlib", text)
        self.assertIn("proc.poll()", text)
        self.assertIn("time.monotonic()", text)
        self.assertIn("isolated_subprocess_kwargs", text)
        self.assertIn("terminate_process_tree", text)
        self.assertIn("os._exit", text)
        self.assertIn("COMPLETION_SETTLE_SECONDS", text)
        self.assertIn("COMPLETION_CHECK_AFTER_SECONDS", text)
        self.assertIn("_discovery_completion_state", text)
        self.assertIn("discovery summary observed", text)
        self.assertNotIn("proc.wait(timeout=timeout)", text)



    def test_test_subprocess_runs_are_timeout_bounded(self):
        missing = []
        for path in sorted((ROOT / "tests").glob("test_*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                is_subprocess_run = (
                    isinstance(func, ast.Attribute)
                    and func.attr == "run"
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "subprocess"
                )
                if is_subprocess_run and not any(keyword.arg == "timeout" for keyword in node.keywords):
                    missing.append(f"{path.name}:{node.lineno}")
        self.assertEqual(missing, [])

    def test_validate_project_compiles_only_project_sources_not_virtualenvs(self):
        text = (ROOT / "scripts/validate_project.py").read_text(encoding="utf-8")
        self.assertIn("EXCLUDED_WORKSPACE_PARTS", text)
        self.assertIn('".venv"', text)
        self.assertIn('".testvenv"', text)
        self.assertIn("compile_project_sources", text)
        self.assertIn("compileall.compile_file", text)
        self.assertNotIn("compileall.compile_dir(str(ROOT)", text)

    def test_workspace_scanners_skip_reviewer_virtualenv_names(self):
        files = [
            "scripts/clean_release_artifacts.py",
            "scripts/check_release_zip.py",
            "services/capability_boundary.py",
            "services/diagnostics.py",
            "services/publication_hygiene.py",
            "services/quality_gate.py",
        ]
        missing = []
        for rel in files:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for token in ('.venv', 'venv', '.testvenv'):
                if token not in text:
                    missing.append(f"{rel}:{token}")
        self.assertEqual(missing, [])


    def test_workspace_scanners_use_pruned_walk_not_plain_rglob(self):
        expected_os_walk = [
            "scripts/clean_release_artifacts.py",
            "scripts/build_release.py",
            "scripts/validate_project.py",
            "services/file_inventory.py",
            "services/release_artifact.py",
            "services/publication_hygiene.py",
            "services/capability_boundary.py",
            "services/diagnostics.py",
            "services/quality_gate.py",
            "tests/test_static_safety.py",
        ]
        missing = []
        for rel in expected_os_walk:
            text = (ROOT / rel).read_text(encoding="utf-8")
            if "os.walk" not in text:
                missing.append(rel)
        self.assertEqual(missing, [])


    def test_current_exit_documentation_matches_wrappers(self):
        docs = [
            ROOT / "RELEASE_NOTES_v27.md",
            ROOT / "VALIDATION_REPORT.md",
            ROOT / "docs" / "quality" / "VALIDATION_HYGIENE.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in docs)
        self.assertNotIn("now return through normal `SystemExit`", combined)
        self.assertIn("os.write()", combined)
        self.assertIn("os._exit()", combined)
        self.assertIn("154/155", combined)
        self.assertIn("runtime-dependency-installed", combined)
        self.assertNotIn("148" + "/149", combined)
        self.assertNotIn("147" + "/148", combined)
        self.assertNotIn("dependency-installed runs can observe " + "148", combined)
        self.assertNotIn("155 tests observed across 21/21 discovered modules, 20 skipped runtime-dependency tests", combined)
        self.assertNotIn("155 tests observed across 21/21 discovered modules in dependency-light mode", combined)
        self.assertIn("154 tests observed across 21/21 discovered modules, 20 skipped runtime-dependency tests", combined)
        for rel in ("scripts/run_clean_validation.py", "scripts/run_full_tests.py"):
            script = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("os.write", script)
            self.assertIn("os._exit", script)



    def test_release_artifact_uses_posix_paths_for_cross_platform_checks(self):
        text = (ROOT / "services" / "release_artifact.py").read_text(encoding="utf-8")
        self.assertIn("path.as_posix() for path in _relative_files", text)
        self.assertIn("rel.as_posix()", text)
        self.assertNotIn("files = {str(path) for path in _relative_files", text)
        self.assertNotIn("findings.append(str(rel))", text)
        self.assertNotIn("return sorted(str(rel)", text)

    def test_quality_gate_exposes_validation_hygiene(self):
        spec = importlib.util.spec_from_file_location("quality_gate", ROOT / "services" / "quality_gate.py")
        self.assertIsNotNone(spec)
        text = (ROOT / "services" / "quality_gate.py").read_text(encoding="utf-8")
        self.assertIn("validation_hygiene_consistent", text)
        self.assertIn("run_validation_hygiene_check", text)



    def test_pipe_free_helper_falls_back_for_os_exit_scripts(self):
        helper = (ROOT / "tests" / "process_helpers.py").read_text(encoding="utf-8")
        self.assertIn("_script_requires_subprocess", helper)
        self.assertIn('"os._exit" in text', helper)
        self.assertIn("return None", helper)

    def test_test_script_checks_use_pipe_free_helper(self):
        helper = (ROOT / "tests" / "process_helpers.py").read_text(encoding="utf-8")
        self.assertIn("runpy.run_path", helper)
        self.assertIn("redirect_stdout", helper)
        self.assertIn("redirect_stderr", helper)
        self.assertIn("isolated_subprocess_kwargs", helper)
        self.assertIn("terminate_process_tree", helper)
        offenders = []
        for path in sorted((ROOT / "tests").glob("test_*.py")):
            if path.name == "test_v23_validation_hygiene.py":
                continue
            text = path.read_text(encoding="utf-8")
            if "subprocess.run(" in text or "capture_output=True" in text:
                offenders.append(path.name)
        self.assertEqual(offenders, [])


    def test_reviewer_commands_avoid_plain_compileall_tree_walk(self):
        docs = [
            ROOT / "README.md",
            ROOT / "Makefile",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in docs)
        self.assertNotIn("python -m compileall -q .", combined)
        self.assertNotIn("$(PYTHON) -m compileall -q .", combined)
        self.assertIn("python scripts/run_clean_validation.py", combined)
        self.assertIn("python scripts/run_full_tests.py", combined)

    def test_cdn_access_language_uses_restricted_not_blocked(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("CDN 접근이 제한되어", readme)
        self.assertNotIn("CDN 접속이 막혀", readme)
        self.assertNotIn("CDN access is blocked", readme)
        self.assertNotIn("CDN-blocked", readme)


if __name__ == "__main__":
    unittest.main()
