# Release Notes v16.0.0-safe

v16 adds release-artifact hygiene checks for reviewer trust.

## What changed

- Added `/api/artifact` for read-only release artifact hygiene status.
- Added `services/release_artifact.py`.
- Added `scripts/check_release_artifact.py` for dependency-light package hygiene verification.
- Added `docs/quality/RELEASE_ARTIFACT.md`.
- Added release artifact checks to the quality gate and validation script.
- Updated current release metadata to `16.0.0-safe`.

## Honest boundary

This release does not add real IPv6 packet capture, packet transmission, network scanning, or detection capability. It improves packaging hygiene and reviewer trust for the existing local simulator.
