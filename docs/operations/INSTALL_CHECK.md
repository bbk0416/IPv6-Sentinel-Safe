# Install Check - 27.0.0-safe

`python scripts/check_requirements.py` validates `requirements.txt` without installing anything.

It confirms that the package declares the local web simulator dependencies and does **not** reintroduce packet capture, packet injection, interception, or platform-specific attack libraries such as `scapy`, `mitmproxy`, `wmi`, `netfilterqueue`, `pcapy`, or `pypcap`.

Recommended order:

```bash
python scripts/check_requirements.py
python scripts/preflight_check.py
pip install -r requirements.txt
python scripts/preflight_check.py --strict
python scripts/run_clean_validation.py
```

The non-strict preflight mode is intended for source-package review before dependencies are installed. It reports missing runtime modules as warnings, not blocking errors. Strict mode is intended after dependency installation.
