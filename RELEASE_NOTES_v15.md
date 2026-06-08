# Release Notes v15.0.0-safe

## Focus

v15 tightens release hygiene rather than adding detection claims.

## Changes

- Added `/api/release` for reviewer-facing release identity status.
- Added `services/release_identity.py` and `scripts/check_release_identity.py`.
- Added `docs/quality/RELEASE_IDENTITY.md`.
- Fixed duplicate release-note declarations in `project_manifest.json`.
- Updated current release metadata to `15.0.0-safe`.
- Added tests that verify release identity consistency.

## Boundary

This remains a local, simulation-only IPv6 security event dashboard. It does not capture packets, inject packets, scan networks, or perform real IPv6 attack detection.
