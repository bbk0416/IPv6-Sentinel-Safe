# Release Notes v26 - 26.0.0-safe

## Focus

v26 adds an explicit capability-boundary gate so reviewers can see what the simulator supports and what it intentionally refuses to do.

## Added

- `/api/capabilities` reviewer endpoint.
- `services/capability_boundary.py` for static capability/non-capability checks.
- `scripts/check_capability_boundary.py` for dependency-light source-package review.
- `docs/quality/CAPABILITY_BOUNDARY.md` explaining the supported simulator scope and explicit non-goals.
- v26 tests for capability boundary and release metadata consistency.

## Still intentionally not included

- No real IPv6 packet capture.
- No packet transmission.
- No real network scanning.
- No DHCPv6/DNS spoofing, MITM, or exploit functionality.
