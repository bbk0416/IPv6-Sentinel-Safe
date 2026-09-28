# Release Notes v27

v27 is the final safe-simulator handoff release line for IPv6 Sentinel Safe.

## Scope

Release ID: `27.0.0-safe`

This project is a local IPv6 security-event simulator for portfolio, education, and demonstration use. It does not capture packets, send packets, scan networks, operate as an IDS/IPS, or claim production detection accuracy.

## What v27 includes

- Flask/Socket.IO dashboard with REST fallback controls
- local sample IPv6 security-event scenarios
- reviewer-facing `/api/reviewer` and quality endpoints
- API/OpenAPI/schema/route/manifest consistency checks
- deterministic file inventory and release ZIP hygiene checks
- publication and capability-boundary checks
- Basic Auth and remote-bind safeguards
- Docker packaging and authenticated container healthcheck
- Linux and Windows GitHub Actions validation

## Validation

The canonical reviewer command is:

```bash
python scripts/run_clean_validation.py
```

For the complete dependency-installed test sweep:

```bash
python scripts/run_full_tests.py
```

The current dependency-installed CI baseline is **161 tests passed**. GitHub Actions validates Python 3.10, 3.11, and 3.12 on Ubuntu and Python 3.12 on Windows. The Ubuntu 3.12 lane also builds the Docker image and requires the authenticated container healthcheck to become healthy.

## Safety boundary

The release intentionally excludes:

- real packet capture
- real packet transmission
- active network scanning
- DHCPv6/DNS spoofing
- MITM
- traffic blocking
- IDS/IPS operation
- exploitation
- production detection-accuracy claims

## Release provenance

The published `27.0.0-safe` GitHub Release is frozen at commit `8821e070`. The current `main` branch contains later documentation and CI maintenance. The published tag and ZIP are not rewritten; current-main integrity is represented by its GitHub Actions result and `docs/release/FILE_INVENTORY.json`.

Detailed implementation history remains available in Git history instead of being repeated in this release note.
