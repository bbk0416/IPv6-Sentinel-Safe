# Capability Boundary Gate

This gate keeps the project honest about what it can and cannot do.

## Supported capabilities

- Local Flask/Socket.IO dashboard for demo use.
- Simulation-only IPv6-style security events.
- Sample asset inventory generation.
- Demo scenario seeding.
- CSV/JSON exports for portfolio review.
- Read-only release validation gates.

## Explicit non-capabilities

- The app does not capture packets.
- The app does not send packets.
- The app does not scan real networks.
- The app does not perform DHCPv6 spoofing, DNS spoofing, MITM, exploit, or isolation actions.
- The app does not provide IDS/IPS detection coverage.

## How to run

```bash
python scripts/check_capability_boundary.py
```

## What this proves

It proves that the package declares the same local simulation-only boundary in source, API docs, manifest, and reviewer-facing documentation.

## What this does not prove

It does not prove real IPv6 monitoring, live packet inspection, detection accuracy, or operational security value. This is a safe educational simulator, not a live network security product.
