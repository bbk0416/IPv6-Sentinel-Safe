# Release Notes v11.0.0-safe

v11 is a trust-and-review cleanup release. It does not add real network monitoring, scanning, packet capture, or packet transmission.

## Added

- `/api/quality` read-only quality gate endpoint.
- `services/quality_gate.py` for version/document/package honesty checks.
- `scripts/release_audit.py` for command-line release review.
- `docs/quality/QUALITY_GATE.md` explaining what the quality gate proves and what it does not prove.
- v11 tests for version consistency and quality gate behavior.

## Changed

- Project metadata updated to `14.0.0-safe`.
- Manifest, OpenAPI, README, validation documents, and completion report updated for v11.
- CI now runs preflight and release audit scripts in addition to the existing validation suite.

## Honest limitation

This remains a local demo simulator. The project still does not inspect real IPv6 traffic and must not be described as an operational IDS/NDR product.
