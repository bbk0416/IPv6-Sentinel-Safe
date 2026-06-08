# Threat Model

## Scope

IPv6 Sentinel Safe is a local-only, simulation-only dashboard. It is designed for education and portfolio review, not live network operations.

## Explicit non-goals

- No real packet capture
- No real packet sending
- No real network scanning
- No DHCP/DNS manipulation
- No privileged OS operations

## Main risks and mitigations

| Risk | Mitigation |
|---|---|
| Accidental remote exposure | Default bind host is `127.0.0.1`; remote bind without auth fails closed |
| Misreading demo data as live data | UI and docs label everything as simulation-only |
| Browser-side injection from local settings | User-controlled text is clamped and escaped before rendering |
| Artifact leakage | Release ZIP excludes logs, data, caches, and virtual environments |

## Reviewer verification

Use `/api/info`, `/api/ready`, and `/api/report.json` to confirm the safe-mode posture.
