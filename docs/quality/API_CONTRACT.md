# API Contract Check

This release includes a read-only API contract gate so reviewers can verify that the project is not relying on stale documentation.

The contract check compares four local sources:

1. Flask route decorators in `app.py`
2. `docs/api/openapi.yaml`
3. `docs/api/API_REFERENCE.md`
4. `project_manifest.json`

Run it with:

```bash
python scripts/check_api_contract.py
```

Or, after installing dependencies and starting the app, call:

```bash
curl http://127.0.0.1:5000/api/contract
```

## What this proves

- Documented API paths match the actual Flask route declarations.
- `project_manifest.json` is not missing API endpoints.
- The human-readable API reference mentions every Flask API path.

## What this does not prove

- It does not prove real IPv6 traffic detection.
- It does not start packet capture, packet transmission, network scanning, or external calls.
- It does not replace browser-based UI testing.

This project remains a local-only, simulation-only IPv6 security event dashboard.
