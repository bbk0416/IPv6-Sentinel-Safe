# Validation Hygiene Gate - 27.0.0-safe

`27.0.0-safe` adds a validation hygiene gate for the safe IPv6 security-event simulator.

## What it checks

- `scripts/validate_project.py` cleans generated cache/bytecode artifacts before and after validation.
- `scripts/run_clean_validation.py` is available as the recommended one-command local validation wrapper.
- `scripts/final_handoff_check.py` still cleans before and after release packaging checks.
- The current workspace does not contain `__pycache__`, `.pyc`, `.pytest_cache`, `.mypy_cache`, or `.ruff_cache` artifacts after the clean validation path.
- README and release documentation explain that this remains a local simulator.

## Recommended command

```bash
python scripts/run_clean_validation.py
```

## What it does not prove

This gate does not prove real IPv6 traffic detection, DHCPv6/DNS monitoring, packet capture, packet sending, or network scanning. It only improves the cleanliness and repeatability of the portfolio validation workflow.

## Pipe-wait hardening

Both the clean wrapper and the validator's internal unittest runner avoid direct pipe capture for long-lived validation children. Child output is redirected to temporary files, children are launched in a new process session, and timeout cleanup kills the whole process group. This is a reviewer-environment reliability measure only; it does not add live IPv6 monitoring, packet capture, packet sending, or network scanning.

## Internal validator subprocess policy

`validate_project.py` avoids direct pipe-captured subprocess checks for the reviewer-facing validation path. Static script checks are imported and executed in-process where practical, while unittest children use file-backed output and process-group timeout cleanup. This keeps the validation command responsive in constrained review environments without changing the simulator's non-network capability boundary.

### Full-test runner exit hygiene

`run_full_tests.py` is optional and heavier than the canonical clean validation wrapper. It now runs the full unittest discovery set in one bounded child process and waits with a polling loop (`proc.poll()` plus `time.monotonic()`) while emitting heartbeat messages. If unittest has already printed its final summary but the child interpreter does not return promptly, the runner waits a very short settle period and then cleans the child process group based on the final pass/fail summary. On timeout it still kills the child process group. This keeps the full-test command responsive in constrained review sandboxes without changing the simulator boundary.

## Windows process-control compatibility

The validation wrappers share `services/process_control.py` so bounded child cleanup is portable. POSIX runners use a new child session and process-group cleanup; Windows runners use `CREATE_NEW_PROCESS_GROUP` when available and a terminate/kill fallback on timeout. This keeps `validate_project.py`, `run_clean_validation.py`, and `run_full_tests.py` aligned across reviewer environments without adding live network monitoring, packet capture, packet sending, or scanning.
