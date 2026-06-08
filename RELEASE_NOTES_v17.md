# Release Notes v17.0.0-safe

v17 improves clean release ZIP building and CI command hygiene.

## What changed

- Added `scripts/clean_release_artifacts.py` to remove generated caches/logs before packaging.
- Added `scripts/check_release_zip.py` to build or inspect a release ZIP and verify that the handoff archive is clean.
- Added `scripts/check_ci_workflow.py` to catch obvious GitHub Actions command drift and malformed multi-command `run:` steps.
- Fixed the CI workflow command block so release identity, artifact, ZIP, and contract checks are explicitly executed.
- Updated `Makefile`, `project_manifest.json`, validation scripts, and quality documentation for the v17 release.

## Honest limitation

This release still does not implement real IPv6 packet capture, traffic analysis, or network detection. It remains a safe local simulator and portfolio project.
