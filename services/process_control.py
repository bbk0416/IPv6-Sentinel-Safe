"""Cross-platform subprocess group helpers for reviewer validation commands.

The validation wrappers need bounded child processes, but POSIX-only process
controls such as ``start_new_session=True`` plus ``os.killpg`` are not portable
on Windows.  This module keeps the runners deterministic on both platforms
without changing the simulator's no-network, local-only behavior.
"""

from __future__ import annotations

import contextlib
import os
import subprocess
import time
from typing import Any


def isolated_subprocess_kwargs() -> dict[str, Any]:
    """Return portable ``subprocess.Popen`` kwargs for an isolated child.

    POSIX uses a new session so the process group can be cleaned as one unit.
    Windows uses ``CREATE_NEW_PROCESS_GROUP`` when available.  The function is
    deliberately small so validation scripts can share the same behavior.
    """
    if os.name == "nt":
        creation_flag = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        return {"creationflags": creation_flag} if creation_flag else {}
    return {"start_new_session": True}


def terminate_process_tree(proc: subprocess.Popen[Any], *, grace_seconds: float = 1.0) -> None:
    """Best-effort cleanup for a timed-out validation child.

    This is intentionally conservative: POSIX kills the child process group;
    Windows first asks the process to terminate and then falls back to kill.
    The helper suppresses lookup errors because timeout cleanup can race with
    natural process exit.
    """
    if proc.poll() is not None:
        return
    if os.name == "nt":
        with contextlib.suppress(Exception):
            proc.terminate()
        deadline = time.monotonic() + grace_seconds
        while proc.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        if proc.poll() is None:
            with contextlib.suppress(Exception):
                proc.kill()
        return

    with contextlib.suppress(Exception):
        os.killpg(proc.pid, 9)
    deadline = time.monotonic() + grace_seconds
    while proc.poll() is None and time.monotonic() < deadline:
        time.sleep(0.05)
    if proc.poll() is None:
        with contextlib.suppress(Exception):
            proc.kill()
