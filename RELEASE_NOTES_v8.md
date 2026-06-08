# Release Notes v8.0.0-safe

v8 focused on service separation, honest limitations, and safer Docker Compose defaults.

## Changed

- Moved deterministic sample assets/events into `services/simulation_catalog.py`.
- Moved dashboard metric state into `services/state.py`.
- Updated project metadata for the v8 safe package line.
- Docker Compose now requires `IPV6_SENTINEL_PASSWORD` to be explicitly provided instead of shipping a weak default password.
- Added architecture and honest-limitations documents.
- Added frontend binding validation script to catch missing DOM IDs and REST fallback drift.

## Safety posture

No real packet capture, packet transmission, network scanning, or traffic manipulation was added. v8 remains simulation-only.
