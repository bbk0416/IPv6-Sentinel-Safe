# Release Notes v9.0.0-safe

## Purpose

v9 is a hardening and honesty pass. It keeps the project strictly simulation-only while reducing the amount of logic concentrated in `app.py` and adding reviewer-facing diagnostics.

## Added

- `services/settings_store.py` for allow-listed, clamped dashboard setting persistence.
- `services/exporters.py` for centralized JSON/CSV export responses.
- `services/diagnostics.py` for runtime/static safety diagnostics.
- `GET /api/diagnostics` for reviewer checks.
- Safer signal-handler registration when the app is instantiated outside the main thread.
- `MAX_CONTENT_LENGTH` limit for API payloads.

## Changed

- Settings load/save moved out of `app.py`.
- Snapshot/report/log export logic moved into service helpers.
- Documentation and manifest updated to v9.

## Still intentionally not included

- Real packet capture.
- Real packet transmission.
- Real network scanning.
- DHCPv6/DNS manipulation.
- IDS/SIEM/NAC-grade detection.

## Validation

Run:

```bash
python -m compileall -q .
node --check static/dashboard.js
python scripts/check_frontend_bindings.py
python -m unittest discover -s tests -v
python scripts/validate_project.py
```
