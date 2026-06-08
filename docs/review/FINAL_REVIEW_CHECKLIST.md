# Final Review Checklist

Release: `27.0.0-safe`

## Before sharing

- [ ] Run `python scripts/run_clean_validation.py`
- [ ] Confirm `/api/info` reports `safe_mode: true`
- [ ] Confirm `/api/ready` returns `ready`
- [ ] Confirm `real_packet_capture_enabled` is false
- [ ] Confirm `real_packet_send_enabled` is false
- [ ] Confirm `real_network_scan_enabled` is false
- [ ] Confirm release ZIP does not contain logs, data, venv, or cache files
- [ ] If exposing beyond localhost, enable Basic Auth and change the default password

## Demo flow

1. Start app with `python app.py` or Docker Compose.
2. Open `http://127.0.0.1:5000`.
3. Click **데모 시나리오**.
4. Click a sample asset to show detail modal.
5. Export CSV, snapshot JSON, or portfolio report.
6. Mention REST fallback if CDN access is restricted in the demo environment.


## Preflight hardening

- Added `/api/preflight` and `scripts/preflight_check.py`.
- Signal handlers are installed at server start time instead of app-construction time.
- Release metadata is updated to `27.0.0-safe`.


## Schema contract

- `/api/schema` and `scripts/check_schema_contract.py` document and validate local simulator payload shapes.
- This is a data-contract improvement only; it does not add real packet capture or detection.


## Release identity gate

`27.0.0-safe` includes `/api/release` and `python scripts/check_release_identity.py` to verify current safe-release consistency across code, OpenAPI, manifest, README, and release handoff documents, while acknowledging the normalized PEP 440 package version in `pyproject.toml`. This is a packaging honesty check, not proof of real network detection.

## Release artifact checklist

Before sharing the ZIP, run:

```bash
python scripts/check_release_artifact.py
```

The check should pass with no runtime/cache artifacts packaged. Passing this check does not mean the project is a real IPv6 detector; it only means the release package is cleaner for review.

## Final packaging checks

Before sharing the ZIP or pushing to GitHub, run:

```bash
python scripts/run_clean_validation.py
python scripts/check_ci_workflow.py
python scripts/check_release_zip.py
```

These checks improve release hygiene only. They do not make the simulator a real network monitoring product.

## Final handoff gate

`27.0.0-safe` adds `python scripts/final_handoff_check.py`, a compact final local handoff gate that delegates to `scripts/run_clean_validation.py` by default. Use `--plan` to print the expanded release checklist, and use `scripts/build_release.py` plus `scripts/check_release_zip.py` for explicit ZIP build/verification. This improves release hygiene but does not add live IPv6 monitoring.


## Release matrix

`27.0.0-safe` adds `python scripts/check_release_matrix.py` and `docs/quality/RELEASE_MATRIX.md` so reviewers can verify safe release markers across code, OpenAPI, manifest, README, and current release notes, plus the normalized package version in `pyproject.toml`. This is a handoff consistency check, not evidence of real IPv6 traffic detection.


## Route hygiene gate

`27.0.0-safe` adds `python scripts/check_route_hygiene.py` and `docs/quality/ROUTE_HYGIENE.md` so reviewers can catch accidental duplicate Flask route decorators and confirm that REST fallback endpoints remain present. This improves release maintainability; it is not evidence of real IPv6 traffic detection.


## 27.0.0-safe validation hygiene gate

`27.0.0-safe` adds a clean validation wrapper and validation hygiene check so reviewers can run the validation suite without leaving generated cache artifacts in the release workspace. This does not add live IPv6 monitoring.
