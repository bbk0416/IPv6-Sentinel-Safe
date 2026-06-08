# Release Notes v21.0.0-safe

v21 is a route hygiene and release-review hardening pass. It does not add real
IPv6 packet capture, packet sending, DNS/DHCP manipulation, or network scanning.

## Added

- `services/route_hygiene.py` for static Flask route-decorator checks.
- `scripts/check_route_hygiene.py` for dependency-light route hygiene validation.
- `docs/quality/ROUTE_HYGIENE.md` explaining the scope and limits of the check.
- v21 tests for route hygiene coverage.

## Fixed

- Removed an accidental duplicate `/api/logs.csv` route decorator.

## Honest limitation

This remains a safe local simulator. The new gate improves route consistency; it
does not make the project a real IPv6 monitoring or detection product.
