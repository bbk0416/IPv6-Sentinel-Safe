# Release Notes v20.0.0-safe

v20 focuses on reviewer handoff traceability rather than adding simulated security features.

## Added

- `services/release_matrix.py` to centralize release-version consistency checks.
- `scripts/check_release_matrix.py` for dependency-light verification of version markers across code, package metadata, OpenAPI, manifest, README, and release notes.
- `docs/quality/RELEASE_MATRIX.md` explaining what the release matrix does and does not prove.
- v20 tests for release matrix coverage.

## Honest boundary

This remains a local IPv6 security-event simulator. It does not capture, inspect, or detect real IPv6 traffic.
