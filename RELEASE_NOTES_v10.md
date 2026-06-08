# Release Notes v10.0.0-safe

v10 is a hardening and review-readiness release. It does not add any real packet capture, packet transmission, network scanning, or traffic manipulation.

## Added

- `GET /api/preflight` for read-only runtime/release readiness checks.
- `scripts/preflight_check.py` for preflight validation without starting the server.
- `services/preflight.py` service layer for dependency, safe-mode, bind/auth, CORS, and review-file checks.
- `docs/operations/PREFLIGHT.md` operator note.
- Tests for preflight API, script output, and signal-handler side effects.

## Changed

- Signal handlers are installed only when `start()` runs, not during `IPv6SentinelApp()` construction. This reduces global side effects in tests and embedded tooling.
- Project metadata updated to `14.0.0-safe`.

## Still intentionally not included

- Real IPv6 packet capture.
- Real network scanning.
- DHCPv6/DNS/ND packet generation.
- Any offensive workflow.
