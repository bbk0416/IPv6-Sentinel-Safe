# Release Matrix Gate - 27.0.0-safe

`27.0.0-safe` adds a dependency-light release matrix gate. The goal is simple: a reviewer should see the same safe release ID in the UI, OpenAPI, README, manifest, and release docs, while `pyproject.toml` clearly uses the normalized PEP 440 package version `27.0.0`.

## Checks

The gate verifies that the current safe release ID appears consistently in:

- `settings.py`
- `pyproject.toml` as normalized package version `27.0.0`
- `project_manifest.json`
- `docs/api/openapi.yaml`
- `README.md`
- `VALIDATION_REPORT.md`
- `PROJECT_COMPLETION_REPORT.md`
- current release notes

It also checks that older release-note files are not accidentally duplicated as the current release note.

## What this does not prove

This does not prove that the simulator is a real IPv6 detector. It only verifies release-ID and package-version metadata consistency for a safer portfolio handoff.
