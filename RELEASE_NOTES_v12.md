# Release Notes v12.0.0-safe

v12 is a validation-honesty release. It does not add real packet capture, packet transmission, network scanning, or traffic manipulation.

## Changed

- `scripts/preflight_check.py` now supports two clear profiles:
  - default `source_package` profile: missing runtime dependencies are warnings, so release ZIP inspection can pass before installation.
  - `--strict` runtime profile: missing runtime dependencies are blocking errors after `pip install -r requirements.txt`.
- `/api/preflight` remains strict because the running server necessarily has runtime dependencies available.
- Added `scripts/check_requirements.py` to validate `requirements.txt` without installing packages.
- Added `docs/operations/INSTALL_CHECK.md` to explain source-package review versus runtime validation.
- Updated version metadata to `14.0.0-safe`.

## Still intentionally not included

- No real IPv6 packet capture.
- No packet injection or network scanning.
- No DHCPv6/DNS/ND/RA manipulation.
- No claim that this is a production IDS/NDR product.
