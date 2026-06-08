# Release Package Manifest

Release: `27.0.0-safe`

## Included

- Flask/Socket.IO safe simulation application
- Dashboard HTML/CSS/JS
- REST fallback endpoints and UI fallback logic
- Runtime and static tests
- Dockerfile and docker-compose.yml
- GitHub Actions CI workflow
- API reference and OpenAPI contract
- Demo script and quick start checklist
- Security policy, checklist, threat model
- Offline preview: `docs/assets/dashboard-preview.png` and `docs/assets/dashboard-preview.svg`

## Excluded by release builder

- `.venv`, `venv`, `.testvenv`
- `__pycache__`, `.pytest_cache`
- `logs`, `data`, `backup`

## Safety guarantee

The package is simulation-only and does not include live packet capture, packet transmission, real network scanning, or network manipulation logic.


## 27.0.0-safe additions

- `/api/diagnostics` reviewer safety endpoint
- `services/settings_store.py`
- `services/exporters.py`
- `services/diagnostics.py`
- Current release note only: `RELEASE_NOTES_v27.md`


## Preflight hardening

- Added `/api/preflight` and `scripts/preflight_check.py`.
- Signal handlers are installed at server start time instead of app-construction time.
- Release metadata is updated to `27.0.0-safe`.

## Quality gate additions

- `services/quality_gate.py`
- `scripts/release_audit.py`
- `docs/quality/QUALITY_GATE.md`
- `/api/quality`
- Historical root release notes before v27 are intentionally omitted from the public handoff.


## Schema contract

- `/api/schema` and `scripts/check_schema_contract.py` document and validate local simulator payload shapes.
- This is a data-contract improvement only; it does not add real packet capture or detection.


## Release identity gate

`27.0.0-safe` includes `/api/release` and `python scripts/check_release_identity.py` to verify current safe-release consistency across code, OpenAPI, manifest, README, and release handoff documents, while acknowledging the normalized PEP 440 package version in `pyproject.toml`. This is a packaging honesty check, not proof of real network detection.

## Release artifact gate

`27.0.0-safe` adds `docs/quality/RELEASE_ARTIFACT.md`, `/api/artifact`, and `python scripts/check_release_artifact.py`. The release artifact gate verifies required handoff files, runtime/cache artifact exclusion, current release-note packaging, run-script clarity, and simulation-only manifest flags.

## Release ZIP gate

`27.0.0-safe` adds `docs/quality/RELEASE_ZIP.md`, `docs/quality/RELEASE_WORKSPACE.md`, `docs/quality/CI_WORKFLOW.md`, and matching scripts for release-package hygiene. The final ZIP should pass `python scripts/check_release_zip.py` and contain no runtime/cache artifacts.

## File inventory gate

`27.0.0-safe` adds `docs/release/FILE_INVENTORY.json`, `docs/quality/FILE_INVENTORY.md`, `/api/integrity`, and `python scripts/check_file_inventory.py`. The gate verifies deterministic file hashes for the clean release tree and helps catch accidental edits or stale handoff files before sharing the ZIP.

## Manifest hygiene gate

`27.0.0-safe` adds `python scripts/final_handoff_check.py`, a compact final local handoff gate that delegates to `scripts/run_clean_validation.py` by default. Use `--plan` to print the expanded release checklist, and use `scripts/build_release.py` plus `scripts/check_release_zip.py` for explicit ZIP build/verification. This improves release hygiene but does not add live IPv6 monitoring.


## 27.0.0-safe release matrix

`27.0.0-safe` adds `python scripts/check_release_matrix.py` and `docs/quality/RELEASE_MATRIX.md` so reviewers can verify safe release markers across code, OpenAPI, manifest, README, and current release notes, plus the normalized package version in `pyproject.toml`. This is a handoff consistency check, not evidence of real IPv6 traffic detection.


## 27.0.0-safe route hygiene gate

`27.0.0-safe` adds `python scripts/check_route_hygiene.py` and `docs/quality/ROUTE_HYGIENE.md` so reviewers can catch accidental duplicate Flask route decorators and confirm that REST fallback endpoints remain present. This improves release maintainability; it is not evidence of real IPv6 traffic detection.

## 27.0.0-safe additions

- `scripts/run_clean_validation.py`
- `scripts/check_validation_hygiene.py`
- `services/validation_hygiene.py`
- `docs/quality/VALIDATION_HYGIENE.md`
- Clean validation workflow documentation is kept under `docs/quality/VALIDATION_HYGIENE.md`.

These files improve clean validation workflow hygiene. They do not add live IPv6 monitoring.

## 27.0.0-safe publication hygiene

The package now includes `docs/quality/PUBLICATION_HYGIENE.md`, `scripts/check_publication_hygiene.py`, and `/api/publication` so reviewers can confirm that obvious personal identifiers, private IPs, user paths, common credential patterns, and stale release-note markers are not present in the public handoff package.


## 27.0.0-safe gate registry

This release includes `docs/quality/GATE_REGISTRY.md`, `services/gate_registry.py`, `scripts/check_gate_registry.py`, and `/api/gates` for reviewer-facing quality-gate registry validation.
