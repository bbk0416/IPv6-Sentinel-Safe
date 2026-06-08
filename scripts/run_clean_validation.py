#!/usr/bin/env python3
"""Run the canonical clean validation flow for the safe simulator package.

This wrapper disables bytecode writes for child checks, cleans generated release
artifacts before validation, runs the main validation script, then cleans again.
It is meant for reviewers who want a single command that does not leave
`__pycache__`, `.pyc`, test cache, log, or runtime data behind.
"""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.clean_release_artifacts import clean  # noqa: E402
from services.validation_hygiene import run_validation_hygiene_check  # noqa: E402
from settings import APP_VERSION  # noqa: E402
from services.process_control import isolated_subprocess_kwargs, terminate_process_tree  # noqa: E402

PYTHON = sys.executable


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _run(name: str, command: list[str], timeout_seconds: int = 120) -> dict[str, Any]:
    """Run a validation step without pipe-handle hangs.

    This wrapper writes child output to temporary files instead of using
    direct pipe capture.  In some constrained sandboxes a validation child can
    finish its work but leave inherited pipe handles open through non-critical
    descendants, making the parent appear stuck while waiting for EOF.  File
    redirection plus process-group timeout cleanup keeps the recommended
    `run_clean_validation.py` command deterministic.
    """
    with tempfile.TemporaryDirectory(prefix="ipv6sentinel-clean-step-") as tmpdir:
        stdout_path = Path(tmpdir) / f"{name}.out"
        stderr_path = Path(tmpdir) / f"{name}.err"
        with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open("w", encoding="utf-8") as stderr_handle:
            proc = subprocess.Popen(
                command,
                cwd=ROOT,
                env=_env(),
                text=True,
                stdout=stdout_handle,
                stderr=stderr_handle,
                **isolated_subprocess_kwargs(),
            )
            try:
                proc.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                terminate_process_tree(proc)
                proc.wait()
                stdout = stdout_path.read_text(encoding="utf-8", errors="ignore")
                stderr = stderr_path.read_text(encoding="utf-8", errors="ignore")
                return {
                    "name": name,
                    "command": " ".join(command),
                    "returncode": 124,
                    "ok": False,
                    "stdout_tail": stdout[-3000:],
                    "stderr_tail": (stderr + "\ntimeout")[-3000:],
                }
        stdout = stdout_path.read_text(encoding="utf-8", errors="ignore")
        stderr = stderr_path.read_text(encoding="utf-8", errors="ignore")
    return {
        "name": name,
        "command": " ".join(command),
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout_tail": stdout[-3000:],
        "stderr_tail": stderr[-3000:],
    }



def _direct_clean_step(name: str) -> dict[str, Any]:
    removed = clean(ROOT)
    return {
        "name": name,
        "command": f"{PYTHON} scripts/clean_release_artifacts.py",
        "returncode": 0,
        "ok": True,
        "stdout_tail": f"[OK] removed {len(removed)} generated artifact(s)\n",
        "stderr_tail": "",
    }


def _direct_validation_hygiene_step() -> dict[str, Any]:
    payload = run_validation_hygiene_check(app_root=ROOT, app_version=APP_VERSION)
    ok = payload.get("status") == "pass"
    return {
        "name": "validation_hygiene",
        "command": f"{PYTHON} scripts/check_validation_hygiene.py",
        "returncode": 0 if ok else 1,
        "ok": ok,
        "stdout_tail": json.dumps(payload, ensure_ascii=False, indent=2)[-3000:],
        "stderr_tail": "",
    }


def main() -> int:
    results = [
        _direct_clean_step("clean_before"),
        _run("validate_project", [PYTHON, "scripts/validate_project.py"]),
        _direct_clean_step("clean_after"),
        _direct_validation_hygiene_step(),
    ]
    failed = [item for item in results if not item["ok"]]
    payload = {
        "status": "pass" if not failed else "fail",
        "version": "27.0.0-safe",
        "mode": "safe_simulation",
        "summary": {"total": len(results), "passed": len(results) - len(failed), "failures": len(failed)},
        "checks": results,
        "notes": [
            "This is the recommended local validation wrapper for the source package.",
            "It does not prove real IPv6 detection; it only validates the safe simulator handoff package.",
        ],
    }
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    os.write(sys.stdout.fileno(), encoded)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    os._exit(main())
