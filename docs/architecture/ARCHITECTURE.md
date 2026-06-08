# Architecture

IPv6 Sentinel Safe is intentionally a **local-only simulator**, not a network sensor.

## Runtime flow

1. `app.py` creates the Flask and Socket.IO application.
2. `services/simulation_catalog.py` provides deterministic sample assets, sample event definitions, and the demo scenario plan.
3. `services/state.py` owns dashboard metric aggregation through `MonitoringStats`.
4. `models/target_manager.py` represents locally observed sample assets.
5. `static/dashboard.js` renders the dashboard through Socket.IO when available and REST fallback when CDN access is restricted.

## What it does not do

- No packet capture.
- No packet transmission.
- No interface scanning.
- No DHCP, DNS, ND, or RA manipulation.
- No host firewall, router, or switch configuration changes.

## Why the current package separates services

Earlier internal iterations worked, but too much sample data and state logic lived directly in `app.py`. The current package keeps the deterministic catalog and state model in `services/` so reviewers can see the boundary between:

- web/API orchestration,
- local simulation data,
- runtime state aggregation,
- UI rendering.

This is still a compact portfolio project, but it is less monolithic and clearer for current review.
