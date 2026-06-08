# Preflight Checks - 27.0.0-safe

`IPv6 Sentinel Safe` includes a read-only preflight check for demo and portfolio review.

Run locally:

```bash
python scripts/preflight_check.py
```

Or query the running app:

```bash
curl http://127.0.0.1:5000/api/preflight
```

The check verifies:

- Python version support
- Runtime dependency availability
- `SAFE_MODE` and `SIMULATION_MODE`
- Real packet capture/send/network scan flags are disabled
- Remote binding is protected by authentication
- CORS is not wildcard by default
- Required portfolio/review documents exist

It does not scan networks, capture packets, transmit packets, or modify host network settings.

## Preflight profiles

`python scripts/preflight_check.py` defaults to the `source_package` profile. This is meant for release ZIP inspection before dependencies are installed. Missing runtime modules are warnings.

`python scripts/preflight_check.py --strict` uses the `runtime` profile. Use it after `pip install -r requirements.txt`; missing runtime modules are blocking errors.

The running `/api/preflight` endpoint is effectively runtime-strict because the Flask server cannot exist without its runtime dependencies.
