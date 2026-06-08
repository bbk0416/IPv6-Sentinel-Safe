# Release Notes v13.0.0-safe

## What changed

v13 focuses on reviewer trust rather than claiming new detection capability.

- Added `services/api_contract.py`.
- Added `scripts/check_api_contract.py`.
- Added `/api/contract` for installed-runtime review.
- Added `docs/quality/API_CONTRACT.md`.
- Updated OpenAPI, API reference, manifest, CI, Makefile, quality gate, and validation flow to include the API contract check.

## Why it matters

Previous versions had good safety checks, but the project still relied on humans to notice whether Flask routes, OpenAPI, API reference, and `project_manifest.json` drifted apart. v13 now checks that automatically.

## Honest limitation

This still does **not** make the project a real IPv6 IDS/NDR, packet monitor, or network security product. It remains a local-only, simulation-only IPv6 security event dashboard for education and portfolio review.
