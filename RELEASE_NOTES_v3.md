# Release Notes v3.0.0-safe

v3 focuses on portfolio-readiness and safer defaults.

## Added

- `/api/info` safe-mode metadata endpoint.
- `/api/snapshot.json` full local dashboard snapshot export.
- Defensive HTTP headers for API and dashboard responses.
- Startup guard that refuses remote binding without authentication.
- Runtime tests for auth, snapshot export, and fail-closed remote binding.
- Stronger static tests for risky library imports and old offensive UI names.
- `SECURITY_CHECKLIST.md` for review before demo or repository upload.

## Changed

- Environment parsing is now defensive. Bad integer/bool `.env` values fall back to safe defaults.
- Basic Auth comparison now uses constant-time comparison.
- Socket.IO Werkzeug allowance is limited to local/debug usage.
- UI now includes a snapshot JSON export button.

## Validation

- `python -m compileall -q .` passed.
- `python -m unittest discover -s tests -v` passed: 12 tests OK.
- Flask app started on `http://127.0.0.1:5000`.
- `/api/health` and `/api/info` returned successful JSON responses.
