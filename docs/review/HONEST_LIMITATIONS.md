# Honest Limitations

This project should be presented as a **safe IPv6 security monitoring simulator**.

## Accurate claims

- It demonstrates a Flask/Socket.IO dashboard pattern.
- It visualizes IPv6-themed security events using local sample data.
- It includes safe-mode controls, API exports, Docker packaging, and CI validation.
- It is suitable for portfolio demos and education.

## Claims to avoid

- Do not call it a real IDS.
- Do not call it a production monitoring product.
- Do not claim it detects live DHCPv6, DNS, ND, or RA activity.
- Do not claim it captures packets or scans networks.

## Product gap

To become a real defensive product, it would need approved passive telemetry ingestion, packet/event parsers, schema validation, storage, alerting, role-based authentication, deployment hardening, observability, and operational testing. Those are intentionally out of scope for this safe portfolio release.
