"""Small script execution helper for unittest modules.

The suite checks many project-local ``scripts/*.py`` entrypoints.  Running those
checks with ``subprocess.run(capture_output=True)`` is unnecessarily slow and can
leave constrained review sandboxes waiting on pipe EOF.  For project-local
Python scripts this helper executes the script entrypoint in-process with
``runpy.run_path`` while capturing stdout/stderr.  A file-backed subprocess
fallback remains available for non-project commands.
"""
from __future__ import annotations

import contextlib
import io
import os
import runpy
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from services.process_control import isolated_subprocess_kwargs, terminate_process_tree


@dataclass(frozen=True)
class CompletedCommand:
    args: Sequence[str]
    returncode: int | str
    stdout: str
    stderr: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def _is_python_executable(arg: str) -> bool:
    name = Path(arg).name.lower()
    return name.startswith("python") or arg == sys.executable


def _normal_exit_code(code: object) -> int:
    if code is None:
        return 0
    if isinstance(code, int):
        return code
    return 1


@contextlib.contextmanager
def _patched_argv_and_cwd(args: Sequence[str], cwd: Path):
    old_argv = sys.argv[:]
    old_cwd = Path.cwd()
    try:
        sys.argv = list(args)
        os.chdir(cwd)
        yield
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)


def _script_requires_subprocess(script_path: Path) -> bool:
    """Keep process-terminating entrypoints out of in-process test helpers."""
    try:
        text = script_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return True
    return "os._exit" in text


def _run_project_python_script(args: Sequence[str], *, cwd: Path, env: Mapping[str, str] | None = None) -> CompletedCommand | None:
    if len(args) < 2 or not _is_python_executable(str(args[0])):
        return None
    script = Path(str(args[1]))
    script_path = script if script.is_absolute() else cwd / script
    try:
        script_path = script_path.resolve()
        cwd_resolved = cwd.resolve()
        script_path.relative_to(cwd_resolved)
    except (OSError, ValueError):
        return None
    if script_path.suffix != ".py" or not script_path.exists():
        return None
    if _script_requires_subprocess(script_path):
        return None

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    old_env: dict[str, str | None] = {}
    if env:
        for key, value in env.items():
            old_env[key] = os.environ.get(key)
            os.environ[key] = value
    try:
        with _patched_argv_and_cwd([str(script_path), *map(str, args[2:])], cwd):
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                try:
                    runpy.run_path(str(script_path), run_name="__main__")
                except SystemExit as exc:
                    returncode = _normal_exit_code(exc.code)
                else:
                    returncode = 0
    finally:
        if env:
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    return CompletedCommand(args=list(args), returncode=returncode, stdout=stdout_buffer.getvalue(), stderr=stderr_buffer.getvalue())


def _run_file_backed_subprocess(
    args: Sequence[str],
    *,
    cwd: Path,
    timeout: int,
    env: Mapping[str, str] | None = None,
) -> CompletedCommand:
    deadline = time.monotonic() + timeout
    with tempfile.TemporaryDirectory(prefix="ipv6sentinel-test-subprocess-") as tmp:
        stdout_path = Path(tmp) / "stdout.txt"
        stderr_path = Path(tmp) / "stderr.txt"
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open("w", encoding="utf-8") as stderr_handle:
            proc = subprocess.Popen(  # noqa: S603 - test helper runs project-local commands only
                list(args),
                cwd=str(cwd),
                env=merged_env,
                text=True,
                stdout=stdout_handle,
                stderr=stderr_handle,
                **isolated_subprocess_kwargs(),
            )
            while True:
                returncode = proc.poll()
                if returncode is not None:
                    break
                if time.monotonic() >= deadline:
                    terminate_process_tree(proc)
                    for _ in range(50):
                        returncode = proc.poll()
                        if returncode is not None:
                            break
                        time.sleep(0.05)
                    else:
                        with contextlib.suppress(ProcessLookupError):
                            proc.kill()
                        returncode = "timeout"
                    if returncode is None:
                        returncode = "timeout"
                    break
                time.sleep(0.05)
        stdout = _read_text(stdout_path)
        stderr = _read_text(stderr_path)
    return CompletedCommand(args=list(args), returncode=returncode, stdout=stdout, stderr=stderr)


def run_command(
    args: Sequence[str],
    *,
    cwd: str | Path,
    timeout: int = 30,
    env: Mapping[str, str] | None = None,
) -> CompletedCommand:
    """Run a project-local script check without pipe-based subprocess capture."""
    cwd_path = Path(cwd)
    in_process_result = _run_project_python_script(args, cwd=cwd_path, env=env)
    if in_process_result is not None:
        return in_process_result
    return _run_file_backed_subprocess(args, cwd=cwd_path, timeout=timeout, env=env)
