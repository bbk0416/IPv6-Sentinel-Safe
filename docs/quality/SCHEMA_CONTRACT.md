# Schema Contract - 27.0.0-safe

This release adds a lightweight, dependency-free data contract for reviewer-facing API payloads.

## What is covered

- `stats`: aggregate dashboard counters
- `asset`: local sample asset records
- `log`: local observation log entries
- `settings`: persisted dashboard preferences

## How to check

```bash
python scripts/check_schema_contract.py
```

The check validates representative local simulator payloads against the schemas in `services/schemas.py`.

## What this does not prove

This contract does **not** prove real IPv6 packet capture, traffic detection, or network monitoring capability. It only proves that the simulator's local JSON payloads are documented and internally consistent.
