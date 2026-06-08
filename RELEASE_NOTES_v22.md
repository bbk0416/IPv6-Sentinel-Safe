# Release Notes v22.0.0-safe

## Focus

v22 is a manifest hygiene release. It does not add real packet capture, packet sending,
network scanning, spoofing, or production detection capability.

## Added

- `/api/manifest` reviewer endpoint.
- `services/manifest_hygiene.py` static manifest consistency checks.
- `scripts/check_manifest_hygiene.py` CLI gate.
- `docs/quality/MANIFEST_HYGIENE.md` documentation.
- Manifest release-note coverage checks so the manifest cannot silently omit shipped release notes.

## Fixed

- Cleaned manifest release-note coverage so existing release note files and manifest declarations match.
- Added manifest hygiene to the quality gate, release audit, final handoff gate, validation script, CI, and Makefile.

## Honest limitation

This remains a local, simulation-only IPv6 security event dashboard. It does not inspect live traffic or operate as a production IDS/NDR tool.
