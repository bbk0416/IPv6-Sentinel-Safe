# Release Notes v24.0.0-safe

## Focus

v24 is a public-release hygiene pass. It does not add real packet capture,
packet sending, network scanning, DHCPv6/DNS interception, or production
security monitoring capability.

## Added

- `/api/publication` reviewer endpoint.
- `services/publication_hygiene.py` static publication hygiene gate.
- `scripts/check_publication_hygiene.py` CLI checker.
- `docs/quality/PUBLICATION_HYGIENE.md` with scope and limitations.
- `tests/test_v24_publication_hygiene.py`.

## What the new gate checks

- No obvious personal identifiers or legacy project names in the public package.
- No plain email addresses in source/docs.
- No private IPv4 addresses or user home paths.
- No common credential/token patterns.
- Current release note and manifest release-note ordering are consistent.

## Honest limitation

Passing v24 hygiene only means the handoff package is cleaner for public review.
It still remains a local, simulation-only IPv6 security event dashboard.
