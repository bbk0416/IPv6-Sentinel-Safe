# Release Notes v14.0.0-safe

## Focus

v14 improves reviewer trust by adding an explicit data/schema contract for the simulator API. This is not a new real-network feature; it documents and validates the local JSON payloads exposed by the dashboard.

## Added

- `/api/schema` reviewer endpoint
- `services/schemas.py` lightweight data-contract definitions
- `scripts/check_schema_contract.py` dependency-free schema contract check
- `docs/quality/SCHEMA_CONTRACT.md`
- Schema contract coverage in validation, CI, Makefile, and the quality gate

## Still intentionally out of scope

- Real packet capture
- Real packet sending
- Real network scanning
- Production IDS/IPS claims
