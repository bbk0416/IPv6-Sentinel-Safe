#!/usr/bin/env python3
"""Repository validation helper for release packaging."""

from __future__ import annotations

import ast
import compileall
import contextlib
import io
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from services.process_control import isolated_subprocess_kwargs, terminate_process_tree  # noqa: E402
BLOCKED_IMPORTS = {"scapy", "mitmproxy", "wmi"}
REQUIRED_FILES = [
    "README.md",
    "SECURITY.md",
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    "requirements.txt",
    "tests/test_static_safety.py",
    "docs/api/API_REFERENCE.md",
    "docs/api/openapi.yaml",
    "docs/demo/DEMO_SCRIPT.md",
    "project_manifest.json",
    "scripts/generate_project_report.py",
    "scripts/build_release.py",
    "docs/demo/PREVIEW.html",
    "docs/assets/dashboard-preview.png",
    "docs/release/RELEASE_PACKAGE_MANIFEST.md",
    "docs/security/THREAT_MODEL.md",
    "docs/review/FINAL_REVIEW_CHECKLIST.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/review/HONEST_LIMITATIONS.md",
    "scripts/check_frontend_bindings.py",
    "docs/operations/PREFLIGHT.md",
    "scripts/preflight_check.py",
    "docs/quality/QUALITY_GATE.md",
    "docs/quality/API_CONTRACT.md",
    "docs/quality/SCHEMA_CONTRACT.md",
    "scripts/release_audit.py",
    "scripts/check_requirements.py",
    "scripts/check_api_contract.py",
    "scripts/check_schema_contract.py",
    "docs/operations/INSTALL_CHECK.md",
    "RELEASE_NOTES_v27.md",
    "docs/quality/RELEASE_IDENTITY.md",
    "scripts/check_release_identity.py",
    "docs/quality/RELEASE_ARTIFACT.md",
    "scripts/check_release_artifact.py",
    "scripts/check_release_zip.py",
    "scripts/clean_release_artifacts.py",
    "scripts/check_ci_workflow.py",
    "docs/quality/RELEASE_ZIP.md",
    "docs/quality/RELEASE_WORKSPACE.md",
    "docs/quality/CI_WORKFLOW.md",
    "docs/quality/FILE_INVENTORY.md",
    "docs/release/FILE_INVENTORY.json",
    "scripts/check_file_inventory.py",
    "scripts/check_release_matrix.py",
    "scripts/check_route_hygiene.py",
    "scripts/check_manifest_hygiene.py",
    "scripts/final_handoff_check.py",
    "docs/quality/FINAL_HANDOFF.md",
    "docs/quality/MANIFEST_HYGIENE.md",
    "docs/quality/VALIDATION_HYGIENE.md",
    "docs/quality/PUBLICATION_HYGIENE.md",
    "docs/quality/GATE_REGISTRY.md",
    "scripts/check_validation_hygiene.py",
    "scripts/check_publication_hygiene.py",
    "scripts/check_gate_registry.py",
    "scripts/check_capability_boundary.py",
    "scripts/run_clean_validation.py",
    "scripts/run_full_tests.py",
    "docs/quality/CAPABILITY_BOUNDARY.md",
    "docs/quality/REVIEWER_HANDOFF.md",
    "scripts/check_reviewer_handoff.py",
]


EXCLUDED_WORKSPACE_PARTS = {".git", ".venv", "venv", "env", ".testvenv", "node_modules"}
GENERATED_ARTIFACT_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def _is_excluded_workspace_path(path: Path) -> bool:
    rel_parts = path.relative_to(ROOT).parts
    return any(part in EXCLUDED_WORKSPACE_PARTS for part in rel_parts)


def _iter_project_python_files() -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_WORKSPACE_PARTS and name not in GENERATED_ARTIFACT_PARTS]
        current = Path(dirpath)
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(current / filename)
    return sorted(files)


def compile_project_sources() -> bool:
    """Compile only project-owned Python files, never reviewer virtualenvs."""
    return all(compileall.compile_file(str(path), quiet=1) for path in _iter_project_python_files())


def cleanup_generated_artifacts() -> None:
    """Remove validation-generated cache artifacts so validation leaves a clean tree."""
    suffixes = {".pyc", ".pyo"}
    targets: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        current = Path(dirpath)
        kept_dirs = []
        for dirname in dirnames:
            child = current / dirname
            if dirname in EXCLUDED_WORKSPACE_PARTS:
                continue
            if dirname in GENERATED_ARTIFACT_PARTS:
                targets.append(child)
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for filename in filenames:
            path = current / filename
            if path.suffix.lower() in suffixes:
                targets.append(path)
    for target in sorted(set(targets), key=lambda item: len(item.parts), reverse=True):
        if not target.exists():
            continue
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()


def check_required_files() -> list[str]:
    return [path for path in REQUIRED_FILES if not (ROOT / path).exists()]


def check_blocked_imports() -> list[str]:
    findings: list[str] = []
    for path in _iter_project_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name.split(".")[0] for alias in node.names}
                for name in names & BLOCKED_IMPORTS:
                    findings.append(f"{path.relative_to(ROOT).as_posix()} imports {name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                name = node.module.split(".")[0]
                if name in BLOCKED_IMPORTS:
                    findings.append(f"{path.relative_to(ROOT).as_posix()} imports {name}")
    return findings



def check_frontend_bindings() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_frontend_bindings.py"
    spec = importlib.util.spec_from_file_location("check_frontend_bindings", script)
    if spec is None or spec.loader is None:
        return ["frontend binding check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["frontend binding check failed"]


def check_release_audit() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "release_audit.py"
    spec = importlib.util.spec_from_file_location("release_audit", script)
    if spec is None or spec.loader is None:
        return ["release audit script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["release audit failed"]





def check_api_contract() -> list[str]:
    # Validates the reviewer-facing /api/contract source/docs consistency gate.
    import importlib.util

    script = ROOT / "scripts" / "check_api_contract.py"
    spec = importlib.util.spec_from_file_location("check_api_contract", script)
    if spec is None or spec.loader is None:
        return ["API contract check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["API contract check failed"]


def check_schema_contract() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_schema_contract.py"
    spec = importlib.util.spec_from_file_location("check_schema_contract", script)
    if spec is None or spec.loader is None:
        return ["schema contract check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["schema contract check failed"]


def check_release_identity() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_release_identity.py"
    spec = importlib.util.spec_from_file_location("check_release_identity", script)
    if spec is None or spec.loader is None:
        return ["release identity check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["release identity check failed"]


def check_release_artifact() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_release_artifact.py"
    spec = importlib.util.spec_from_file_location("check_release_artifact", script)
    if spec is None or spec.loader is None:
        return ["release artifact check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["release artifact check failed"]



def check_release_zip() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_release_zip.py"
    spec = importlib.util.spec_from_file_location("check_release_zip", script)
    if spec is None or spec.loader is None:
        return ["release zip check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["release zip check failed"]


def check_ci_workflow() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_ci_workflow.py"
    spec = importlib.util.spec_from_file_location("check_ci_workflow", script)
    if spec is None or spec.loader is None:
        return ["CI workflow check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["CI workflow check failed"]

def check_requirements_file() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_requirements.py"
    spec = importlib.util.spec_from_file_location("check_requirements", script)
    if spec is None or spec.loader is None:
        return ["requirements check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["requirements check failed"]



def check_file_inventory() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_file_inventory.py"
    spec = importlib.util.spec_from_file_location("check_file_inventory", script)
    if spec is None or spec.loader is None:
        return ["file inventory check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["file inventory check failed"]


def check_final_handoff_plan() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "final_handoff_check.py"
    spec = importlib.util.spec_from_file_location("final_handoff_check", script)
    if spec is None or spec.loader is None:
        return ["final handoff plan check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        steps = module.planned_steps()
    except Exception as exc:
        return [f"final handoff plan check failed: {exc}"]
    names = {step.get("name") for step in steps if isinstance(step, dict)}
    required = {"clean_workspace_before", "refresh_file_inventory", "check_temp_release_zip"}
    missing = sorted(required - names)
    return ["final handoff plan missing: " + ", ".join(missing)] if missing else []



def check_release_matrix() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_release_matrix.py"
    spec = importlib.util.spec_from_file_location("check_release_matrix", script)
    if spec is None or spec.loader is None:
        return ["release matrix check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["release matrix check failed"]


def check_route_hygiene() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_route_hygiene.py"
    spec = importlib.util.spec_from_file_location("check_route_hygiene", script)
    if spec is None or spec.loader is None:
        return ["route hygiene check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["route hygiene check failed"]


def check_manifest_hygiene() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_manifest_hygiene.py"
    spec = importlib.util.spec_from_file_location("check_manifest_hygiene", script)
    if spec is None or spec.loader is None:
        return ["manifest hygiene check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["manifest hygiene check failed"]



def check_validation_hygiene() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_validation_hygiene.py"
    spec = importlib.util.spec_from_file_location("check_validation_hygiene", script)
    if spec is None or spec.loader is None:
        return ["validation hygiene check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["validation hygiene check failed"]




def check_publication_hygiene() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_publication_hygiene.py"
    spec = importlib.util.spec_from_file_location("check_publication_hygiene", script)
    if spec is None or spec.loader is None:
        return ["publication hygiene check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["publication hygiene check failed"]


def check_capability_boundary() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_capability_boundary.py"
    spec = importlib.util.spec_from_file_location("check_capability_boundary", script)
    if spec is None or spec.loader is None:
        return ["capability boundary check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["capability boundary check failed"]


def check_gate_registry() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_gate_registry.py"
    spec = importlib.util.spec_from_file_location("check_gate_registry", script)
    if spec is None or spec.loader is None:
        return ["gate registry check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["gate registry check failed"]

def check_reviewer_handoff() -> list[str]:
    import importlib.util

    script = ROOT / "scripts" / "check_reviewer_handoff.py"
    spec = importlib.util.spec_from_file_location("check_reviewer_handoff", script)
    if spec is None or spec.loader is None:
        return ["reviewer handoff check script could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    return [] if result == 0 else ["reviewer handoff check failed"]


def _run_unittest_module(module: str, timeout_seconds: int = 60) -> tuple[bool, str]:
    """Run one unittest module with bounded, file-backed subprocess cleanup.

    Do not use stdout/stderr PIPE capture here.  In constrained review
    sandboxes, non-critical descendants can keep inherited pipe handles open
    after the unittest child has finished, which makes ``communicate()`` look
    stuck while waiting for EOF.  File redirection plus process-group timeout
    cleanup keeps ``validate_project.py`` deterministic as a reviewer command.
    """
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("IPV6_SENTINEL_LOG_CONSOLE_ENABLED", "0")
    env.setdefault("IPV6_SENTINEL_LOG_FILE_ENABLED", "0")
    with tempfile.TemporaryDirectory(prefix="ipv6sentinel-validate-test-") as tmpdir:
        stdout_path = Path(tmpdir) / f"{module.replace('.', '_')}.out"
        stderr_path = Path(tmpdir) / f"{module.replace('.', '_')}.err"
        with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open("w", encoding="utf-8") as stderr_handle:
            proc = subprocess.Popen(
                [sys.executable, "-m", "unittest", module, "-q"],
                cwd=ROOT,
                env=env,
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
                **isolated_subprocess_kwargs(),
            )
            try:
                proc.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                terminate_process_tree(proc)
                proc.wait()
                stdout = stdout_path.read_text(encoding="utf-8", errors="ignore") if stdout_path.exists() else ""
                stderr = stderr_path.read_text(encoding="utf-8", errors="ignore") if stderr_path.exists() else ""
                detail = (stderr or stdout or "").strip()
                return False, f"{module} timed out after {timeout_seconds}s" + (f": {detail[-500:]}" if detail else "")
        stdout = stdout_path.read_text(encoding="utf-8", errors="ignore") if stdout_path.exists() else ""
        stderr = stderr_path.read_text(encoding="utf-8", errors="ignore") if stderr_path.exists() else ""
    if proc.returncode != 0:
        detail = (stderr or stdout or "").strip()
        return False, f"{module} failed" + (f": {detail[-500:]}" if detail else "")
    return True, ""


def run_unittests() -> bool:
    """Run a lightweight validation-test subset with bounded child cleanup.

    The reviewer-safe validation suite should be run with `python scripts/run_clean_validation.py`.
    This release validation entrypoint intentionally runs the static packaging,
    static safety, and current-release hygiene tests only so the handoff command
    remains fast and avoids subprocess-heavy recursion in constrained review
    sandboxes.
    """
    modules = [
        "tests.test_packaging",
        "tests.test_static_safety",
        "tests.test_v27_publication_hygiene",
        "tests.test_v27_capability_boundary",
    ]
    for module in modules:
        ok, detail = _run_unittest_module(module)
        if not ok:
            print(f"[FAIL] unittest module failed: {detail}")
            return False
    return True


def main() -> int:
    cleanup_generated_artifacts()
    try:
        errors: list[str] = []
        errors.extend(f"missing required file: {item}" for item in check_required_files())
        errors.extend(check_blocked_imports())
        errors.extend(check_frontend_bindings())
        errors.extend(check_release_audit())
        errors.extend(check_api_contract())
        errors.extend(check_requirements_file())
        errors.extend(check_schema_contract())
        errors.extend(check_release_identity())
        errors.extend(check_release_artifact())
        errors.extend(check_release_zip())
        errors.extend(check_ci_workflow())
        errors.extend(check_file_inventory())
        errors.extend(check_release_matrix())
        errors.extend(check_route_hygiene())
        errors.extend(check_manifest_hygiene())
        errors.extend(check_validation_hygiene())
        errors.extend(check_publication_hygiene())
        errors.extend(check_gate_registry())
        errors.extend(check_capability_boundary())
        errors.extend(check_reviewer_handoff())
        errors.extend(check_final_handoff_plan())

        if not compile_project_sources():
            errors.append("project source compilation failed")

        if errors:
            for error in errors:
                print(f"[FAIL] {error}")
            return 1

        if not run_unittests():
            return 1

        print("[OK] project validation passed")
        return 0
    finally:
        cleanup_generated_artifacts()


if __name__ == "__main__":
    exit_code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    # Avoid constrained review sandboxes hanging on non-critical handles left by
    # imported validation/runtime dependencies after successful validation.
    os._exit(exit_code)
