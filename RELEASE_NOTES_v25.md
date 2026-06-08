# RELEASE_NOTES_v25.md — 25.0.0-safe

## Purpose

v25 is a maintenance-focused release. It does not add real packet
capture, packet sending, active network scanning, or production IPv6 detection.
It adds a central quality-gate registry so reviewers can verify that the many
release checks, scripts, documents, and reviewer-facing endpoints stay aligned.

## Added

- `/api/gates` read-only gate registry endpoint.
- `services/gate_registry.py` central registry for release/review gates.
- `scripts/check_gate_registry.py` for source-package validation without running the server.
- `docs/quality/GATE_REGISTRY.md` explaining the registry and its limits.
- `tests/test_v25_gate_registry.py` focused tests for the new registry gate.

## Honest limitation

The project remains a local safe simulator. It is suitable as a portfolio or
education package, not as a real IPv6 monitoring product.
