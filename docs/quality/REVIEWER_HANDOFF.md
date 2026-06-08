# Reviewer Handoff Gate

This gate gives reviewers one honest, low-friction entry point for understanding the package.

## What it checks

- The project exposes `/api/reviewer`.
- The endpoint is listed in `project_manifest.json`, the API reference, and OpenAPI.
- The README includes a minimal validation/run sequence.
- The review documents clearly state the simulator boundary.
- The package states non-claims: it does **not capture packets**, does **not send packets**, does **not scan**, and is **not a live IPv6 IDS/IPS or network security product**.

## What it does not check

- It does not prove real network detection.
- It does not start a packet sniffer.
- It does not scan networks.
- It does not validate browser rendering pixel by pixel.

Use this gate as a reviewer convenience check, not as evidence of production security-monitoring capability.
