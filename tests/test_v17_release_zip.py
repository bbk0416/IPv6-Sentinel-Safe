import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
from process_helpers import run_command


class V17ReleaseZipTests(unittest.TestCase):
    def test_release_zip_script_builds_clean_archive(self):
        result = run_command(
            [sys.executable, "scripts/check_release_zip.py"],
            cwd=ROOT,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "27.0.0-safe")

    def test_build_release_excludes_generated_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            zip_path = Path(temp) / "candidate.zip"
            result = run_command(
                [sys.executable, "scripts/build_release.py", "--output", str(zip_path)],
                cwd=ROOT,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
            self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))
            self.assertTrue(any(name.endswith("RELEASE_NOTES_v27.md") for name in names))
            self.assertTrue(any(name.endswith("docs/quality/RELEASE_ZIP.md") for name in names))



    def test_build_release_uses_platform_stable_posix_member_order(self):
        import importlib.util

        script = ROOT / "scripts" / "build_release.py"
        spec = importlib.util.spec_from_file_location("build_release", script)
        self.assertIsNotNone(spec)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module._release_sort_key(ROOT / "docs" / "api" / "openapi.yaml"), "docs/api/openapi.yaml")

    def test_build_release_excludes_nested_zip_files(self):
        leftover = ROOT / "nested-leftover.zip"
        try:
            leftover.write_bytes(b"not a release artifact")
            with tempfile.TemporaryDirectory() as temp:
                zip_path = Path(temp) / "candidate.zip"
                result = run_command(
                    [sys.executable, "scripts/build_release.py", "--output", str(zip_path)],
                    cwd=ROOT,
                    timeout=60,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                with zipfile.ZipFile(zip_path) as zf:
                    names = zf.namelist()
                self.assertFalse(any(name.endswith(".zip") for name in names))
        finally:
            leftover.unlink(missing_ok=True)

    def test_release_zip_inspector_rejects_nested_zip_members(self):
        with tempfile.TemporaryDirectory() as temp:
            zip_path = Path(temp) / "candidate.zip"
            result = run_command(
                [sys.executable, "scripts/build_release.py", "--output", str(zip_path)],
                cwd=ROOT,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(zip_path, "a", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("IPv6Sentinel_SAFE_v27_FINAL/nested-leftover.zip", b"nested zip placeholder")
            result = run_command(
                [sys.executable, "scripts/check_release_zip.py", str(zip_path)],
                cwd=ROOT,
                timeout=60,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertIn("nested-leftover.zip", " ".join(payload["errors"]))

    def test_ci_workflow_sanity_check_passes(self):
        result = run_command(
            [sys.executable, "scripts/check_ci_workflow.py"],
            cwd=ROOT,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")

    def test_v17_manifest_declares_current_release_note_once(self):
        manifest = json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "27.0.0-safe")
        self.assertEqual(manifest["release_notes"].count("RELEASE_NOTES_v27.md"), 1)
        self.assertEqual(manifest["release_notes"], ["RELEASE_NOTES_v27.md"])
        self.assertIn("docs/quality/RELEASE_ZIP.md", manifest["included_final_docs"])
