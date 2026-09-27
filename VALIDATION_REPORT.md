# Validation Report - 27.0.0-safe

## Scope

This report is the current validation summary for IPv6 Sentinel Safe. It covers source/package consistency, automated tests, release hygiene, deployment packaging, and the simulator safety boundary.

It does **not** validate real IPv6 traffic detection, packet capture, packet transmission, active network scanning, IDS/IPS effectiveness, or production monitoring accuracy.

## Canonical validation

Run the repository's primary validation command first:

```bash
python scripts/run_clean_validation.py
```

For full dependency-installed unittest discovery:

```bash
python scripts/run_full_tests.py
```

For the expanded handoff checklist:

```bash
python scripts/final_handoff_check.py --plan
```

## Current automated environments

The GitHub Actions workflow validates the current tree in these standard environments:

- Ubuntu `ubuntu-latest`: Python 3.10, 3.11, 3.12
- Windows `windows-latest`: Python 3.12

The Linux matrix also builds the Docker image. The Python 3.12 Linux job starts the auth-enabled container and requires Docker `Health.Status=healthy`.

## Current release baseline

The dependency-installed full-test baseline is:

```txt
full unittest discovery: 161 tests passed
```

The release gates also require:

```txt
requirements manifest: pass
file inventory: pass
clean validation: pass
project validation: pass
release audit: pass
release ZIP hygiene: pass
```

`docs/release/FILE_INVENTORY.json` is the deterministic source-package inventory. Text files are hashed with LF-normalized line endings so ordinary Windows/macOS/Linux checkout line-ending differences do not change the package digest.

## Security and deployment checks

Current checks cover the following repository claims:

- default loopback binding
- fail-closed remote binding unless authentication is configured or an explicit insecure-lab override is used
- minimum 12-character Basic Auth password when authentication is enabled
- Socket.IO authentication using the same Basic Auth credentials
- explicit CORS origins by default
- browser mutation checks using Fetch Metadata and Origin/Referer validation
- defensive browser security headers
- non-root container runtime
- reproducible container dependency inputs
- authenticated Docker readiness healthcheck
- release artifact, publication, manifest, route, schema, API-contract, capability-boundary, and reviewer-handoff consistency

## Safety boundary

The repository intentionally keeps these capabilities disabled or absent:

- real packet capture
- real packet transmission
- active network scanning
- DHCPv6/DNS spoofing
- MITM
- IDS/IPS blocking
- exploitation
- production detection-accuracy measurement

The dashboard data is generated from local sample/simulation state.

## Evidence and history

Current reviewer-facing evidence is kept in the active source, CI workflow, tests, and quality-gate documents. Earlier iterative validation notes are preserved in Git history rather than repeated in this current-state report.

The source of truth for current checks is:

- `.github/workflows/ci.yml`
- `scripts/run_clean_validation.py`
- `scripts/run_full_tests.py`
- `scripts/final_handoff_check.py`
- `docs/quality/`
- `docs/release/FILE_INVENTORY.json`
