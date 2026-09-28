# Changelog

## 27.0.0-safe

Current portfolio handoff release line.

- Finalized the project as a local IPv6 security-event simulator with no packet capture, packet sending, or active network scanning.
- Added reviewer-facing API, schema, route, manifest, capability-boundary, publication, release-artifact, and file-inventory checks.
- Added deterministic release ZIP and source-tree integrity validation.
- Hardened remote binding, Basic Auth, browser mutation checks, CORS defaults, and security headers.
- Added Docker packaging with authenticated container health verification.
- Added GitHub Actions validation on Ubuntu Python 3.10/3.11/3.12 and Windows Python 3.12.
- Current dependency-installed full unittest discovery baseline: 161 tests passed.
- Pinned GitHub Actions to full commit SHAs, restricted workflow token permissions to `contents: read`, and disabled persisted checkout credentials.
- Consolidated current reviewer documentation and preserved the published `27.0.0-safe` release snapshot without retagging it.

## Earlier iterations

Earlier revisions established the safe-simulation boundary, local dashboard, export APIs, authentication, Docker support, and validation tooling. Detailed intermediate changes remain available in Git history rather than being repeated in the current handoff tree.
