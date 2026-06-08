# Release Notes v19.0.0-safe

v19 is a final handoff hardening pass. It does not add real IPv6 packet capture,
packet transmission, network scanning, or operational intrusion detection.

## Added

- `scripts/final_handoff_check.py` for one-command release handoff validation.
- `docs/quality/FINAL_HANDOFF.md` explaining the final handoff gate and its limits.
- `tests/test_v20_final_handoff.py` to verify the handoff checker and documentation.

## Improved

- Release validation now has a dedicated final handoff path that cleans generated
  caches, validates source contracts, builds a temporary ZIP, checks ZIP hygiene,
  and refreshes/validates the file inventory flow.
- Makefile and CI expose the final handoff check explicitly.

## Still intentionally out of scope

- No live packet capture.
- No packet injection.
- No DHCPv6/DNS spoofing.
- No real network scanning.
- No operational IDS/IPS claim.
