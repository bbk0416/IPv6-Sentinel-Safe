# Security Policy

IPv6 Sentinel Safe is intentionally simulation-only. It must not be modified to capture, transmit, alter, or probe traffic on networks you do not own or administer.

## Safe defaults

- Binds to `127.0.0.1` by default.
- Does not include packet crafting or interception dependencies.
- Uses local sample data for assets and observations.
- Provides optional Basic Auth through environment variables.

## Reporting issues

For this portfolio/demo package, report issues by opening a private issue or by documenting the reproduction steps in your own repository. Include OS, Python version, command used, and relevant logs.
