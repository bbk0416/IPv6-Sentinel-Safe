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
| Accidental remote exposure | Default app bind is `127.0.0.1`; Docker Compose publishes port 5000 to host loopback only; remote bind without auth fails closed |
| Basic Auth credential disclosure over cleartext HTTP | Remote access guidance requires HTTPS termination at a same-host reverse proxy; port 5000 is not exposed directly |
| Cross-site authenticated browser mutation | Authenticated state-changing REST requests check Fetch Metadata and Origin/Referer; public HTTPS Origin must be explicitly configured |
| Reverse-proxy Origin mismatch | `IPV6_SENTINEL_CORS` is set to the exact public HTTPS Origin instead of trusting arbitrary forwarded headers |
| TLS key or password leakage | TLS private keys and authentication secrets stay outside the repository and are supplied by the deployment environment |
| Misreading demo data as live data | UI and docs label everything as simulation-only |
| Browser-side injection from local settings | User-controlled text is clamped and escaped before rendering |
| Artifact leakage | Release ZIP excludes logs, data, caches, and virtual environments |

## Reviewer verification

Use `/api/info`, `/api/ready`, and `/api/report.json` to confirm the safe-mode posture.
