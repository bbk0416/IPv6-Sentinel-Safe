# Release Notes v18.0.0-safe

v18 is a release-integrity hardening pass. It does not add real packet capture,
packet sending, scanning, or detection. The project remains a local educational
IPv6 security event simulator.

## Added

- `/api/integrity` reviewer endpoint for file inventory integrity status.
- `services/file_inventory.py` for deterministic source-tree hashing.
- `scripts/check_file_inventory.py` for dependency-free inventory validation.
- `docs/release/FILE_INVENTORY.json` generated from the clean source tree.
- `docs/quality/FILE_INVENTORY.md` explaining what the integrity gate proves and does not prove.

## Improved

- Quality gate, release audit, validation script, API docs, OpenAPI, and manifest now include the file inventory integrity gate.
- Release metadata updated to `20.0.0-safe`.

## Boundary

This release still does not perform real IPv6 traffic monitoring. It is safe, local, and simulation-only.
