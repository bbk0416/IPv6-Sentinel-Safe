# Quick Start Checklist

Release: `27.0.0-safe`

## Local run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open: `http://127.0.0.1:5000`

## Demo buttons

- **데모 시나리오**: fills the dashboard with deterministic sample data.
- **샘플 자산 생성**: creates local example assets.
- **스냅샷 JSON 저장**: exports current dashboard state.
- **포트폴리오 리포트**: exports reviewer-friendly safety summary.

## CDN-restricted environments

If the browser cannot load Socket.IO/Chart.js/Bootstrap from CDN, the current v27 dashboard automatically switches to **REST fallback** mode. Basic demo controls still work through local API endpoints.

## Final safety check

```bash
python scripts/run_clean_validation.py
```


## Preflight hardening

- Added `/api/preflight` and `scripts/preflight_check.py`.
- Signal handlers are installed at server start time instead of app-construction time.
- Release metadata is updated to `27.0.0-safe`.


## Schema contract

- `/api/schema` and `scripts/check_schema_contract.py` document and validate local simulator payload shapes.
- This is a data-contract improvement only; it does not add real packet capture or detection.
