# Release Notes v7.0.0-safe

v7 is the final handoff-focused release of IPv6 Sentinel Safe.

## Added

- REST fallback control endpoints for CDN-restricted environments:
  - `POST /api/monitoring/start`
  - `POST /api/monitoring/stop`
  - `POST /api/assets/generate`
  - `POST /api/logs/clear`
  - `POST /api/simulation/speed`
- Dashboard auto-fallback when the Socket.IO browser client cannot be loaded.
- Offline PNG dashboard preview at `docs/assets/dashboard-preview.png`.
- Updated OpenAPI contract for all v7 endpoints.
- Additional static/package/runtime tests for fallback behavior.

## Safety posture

The project remains simulation-only. It does not capture packets, send packets, scan real networks, change host networking, or perform live network manipulation.

## Recommended final checks

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
python scripts/validate_project.py
python scripts/build_release.py --output ../IPv6Sentinel_SAFE_v7_release.zip
```
