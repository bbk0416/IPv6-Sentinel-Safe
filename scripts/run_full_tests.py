#!/usr/bin/env python3
"""Run the full unittest suite with one bounded discovery subprocess.

This optional reviewer command is safer than an unwrapped raw
``python -m unittest discover`` invocation in constrained sandboxes: it cleans
before and after the run, disables bytecode and runtime logs, places runtime data
in a temporary directory, writes unittest output to files, emits short heartbeat
messages while discovery runs, and kills the whole discovery process group if it
exceeds its timeout.  The canonical quick validation command remains
``python scripts/run_clean_validation.py``.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.clean_release_artifacts import clean  # noqa: E402
from services.process_control import isolated_subprocess_kwargs, terminate_process_tree  # noqa: E402

DISCOVERY_TIMEOUT_SECONDS = 90
HEARTBEAT_SECONDS = 3
COMPLETION_CHECK_AFTER_SECONDS = 30
COMPLETION_SETTLE_SECONDS = 0.25



def _extract_count(stderr: str) -> int:
    match = re.search(r"Ran\s+(\d+)\s+tests?", stderr)
    return int(match.group(1)) if match else 0


def _discovery_completion_state(stderr_path: Path) -> str | None:
    """Return pass/fail when unittest has printed its final summary.

    Some constrained review sandboxes can leave the Python child process around
    briefly after unittest has already emitted its final summary.  We use the
    file-backed stderr summary as a completion marker, then give the child a
    short grace period before process-group cleanup.  This keeps the optional
    full-test runner responsive without hiding real test failures.
    """
    if not stderr_path.exists():
        return None
    text = stderr_path.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"Ran\s+\d+\s+tests?", text):
        return None
    if "\nOK" in text or text.rstrip().endswith("OK") or "OK (skipped=" in text:
        return "pass"
    if "FAILED" in text or "ERROR" in text:
        return "fail"
    return None


def _tail(text: str, limit: int = 4000) -> str:
    return text[-limit:] if len(text) > limit else text


def _test_modules() -> list[str]:
    return [f"tests.{path.stem}" for path in sorted((ROOT / "tests").glob("test_*.py"))]


def _wait_for_process(proc: subprocess.Popen[object], *, timeout: int, stderr_path: Path) -> int | str:
    """Wait with polling and reviewer-visible heartbeat output.

    Running discovery as one child process is materially faster than spawning a
    new Python interpreter for every test module in constrained sandboxes.  The
    child is still bounded by a process-group timeout, and heartbeat messages
    make it clear that the optional deep test sweep is still progressing.  If
    unittest has already emitted a final pass/fail summary but the interpreter
    does not return promptly, the runner waits a short settle period and then
    cleans the process group based on that final summary.
    """
    deadline = time.monotonic() + timeout
    last_heartbeat = 0.0
    completion_state: str | None = None
    completion_seen_at: float | None = None
    while True:
        returncode = proc.poll()
        if returncode is not None:
            return returncode
        now = time.monotonic()
        elapsed = now - (deadline - timeout)
        current_state = None
        if elapsed >= COMPLETION_CHECK_AFTER_SECONDS:
            current_state = _discovery_completion_state(stderr_path)
        if current_state and completion_state is None:
            completion_state = current_state
            completion_seen_at = now
            print(
                f"[run_full_tests] discovery summary observed ({completion_state}); waiting for child exit",
                file=sys.stderr,
                flush=True,
            )
        if completion_state and completion_seen_at is not None and now - completion_seen_at >= COMPLETION_SETTLE_SECONDS:
            print("[run_full_tests] discovery child settle timeout; cleaning process group", file=sys.stderr, flush=True)
            terminate_process_tree(proc)
            for _ in range(50):
                returncode = proc.poll()
                if returncode is not None:
                    return 0 if completion_state == "pass" else 1
                time.sleep(0.1)
            with contextlib.suppress(ProcessLookupError):
                proc.kill()
            return 0 if completion_state == "pass" else 1
        if elapsed - last_heartbeat >= HEARTBEAT_SECONDS:
            print(f"[run_full_tests] discovery still running ({int(elapsed)}s)", file=sys.stderr, flush=True)
            last_heartbeat = elapsed
        if now >= deadline:
            print("[run_full_tests] discovery timeout; killing process group", file=sys.stderr, flush=True)
            terminate_process_tree(proc)
            for _ in range(50):
                returncode = proc.poll()
                if returncode is not None:
                    return "timeout"
                time.sleep(0.1)
            with contextlib.suppress(ProcessLookupError):
                proc.kill()
            return "timeout"
        time.sleep(0.1)


def run_suite(*, timeout: int = DISCOVERY_TIMEOUT_SECONDS) -> dict[str, object]:
    """Run unittest discovery in one bounded child process."""
    modules = _test_modules()
    with tempfile.TemporaryDirectory(prefix="ipv6sentinel-full-tests-") as tmpdir:
        data_root = Path(tmpdir) / "runtime-data"
        capture_dir = Path(tmpdir) / "unittest-output"
        capture_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = capture_dir / "discover.out"
        stderr_path = capture_dir / "discover.err"
        env = os.environ.copy()
        env.update({
            "PYTHONDONTWRITEBYTECODE": "1",
            "IPV6_SENTINEL_LOG_CONSOLE_ENABLED": "0",
            "IPV6_SENTINEL_LOG_FILE_ENABLED": "0",
            "IPV6_SENTINEL_DATA_DIR": str(data_root),
        })
        print("[run_full_tests] running full unittest discovery in one bounded child", file=sys.stderr, flush=True)
        with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open("w", encoding="utf-8") as stderr_handle:
            proc = subprocess.Popen(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=stdout_handle,
                stderr=stderr_handle,
                **isolated_subprocess_kwargs(),
            )
            returncode = _wait_for_process(proc, timeout=timeout, stderr_path=stderr_path)
        stdout = stdout_path.read_text(encoding="utf-8", errors="ignore") if stdout_path.exists() else ""
        stderr = stderr_path.read_text(encoding="utf-8", errors="ignore") if stderr_path.exists() else ""

    timed_out = returncode == "timeout"
    ok = returncode == 0
    return {
        "ok": ok,
        "returncode": returncode,
        "tests": _extract_count(stderr),
        "modules_total": len(modules),
        "modules_run": len(modules) if ok else 0,
        "discovery_mode": "single_bounded_child",
        "module_results": [
            {
                "module": "unittest_discover",
                "ok": ok,
                "returncode": returncode,
                "tests": _extract_count(stderr),
                "stdout_tail": _tail(stdout),
                "stderr_tail": _tail((stderr or "") + ("\ntimeout" if timed_out else "")),
            }
        ],
        "stdout_tail": _tail(stdout),
        "stderr_tail": _tail((stderr or "") + ("\ntimeout" if timed_out else "")),
    }


def main() -> int:
    print("[run_full_tests] cleaning workspace", file=sys.stderr, flush=True)
    clean(ROOT)
    try:
        result = run_suite()
    finally:
        print("[run_full_tests] cleaning workspace after tests", file=sys.stderr, flush=True)
        clean(ROOT)

    payload = {
        "status": "pass" if result["ok"] else "fail",
        "mode": "safe_simulation",
        "summary": {
            "tests_observed": int(result.get("tests", 0)),
            "modules_run": int(result.get("modules_run", 0)),
            "modules_total": int(result.get("modules_total", 0)),
            "returncode": result.get("returncode"),
            "discovery_mode": result.get("discovery_mode"),
        },
        "result": result,
        "notes": [
            "Use python scripts/run_clean_validation.py for the canonical quick handoff check.",
            "This optional command runs the full unittest discovery set in one bounded child process with heartbeat output and process-group timeout cleanup.",
            "It does not add live IPv6 packet capture, packet sending, network scanning, or production detection capability.",
        ],
    }
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    os.write(sys.stdout.fileno(), encoded)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    os._exit(main())
