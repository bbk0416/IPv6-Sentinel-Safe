# Route Hygiene Gate - 27.0.0-safe

`27.0.0-safe` adds a static Flask route hygiene check:

```bash
python scripts/check_route_hygiene.py
```

The gate checks that:

- Flask route decorators exist in `app.py`
- the same route is not accidentally declared twice
- REST fallback endpoints remain present for offline/CDN-restricted dashboard use

This is a packaging and maintainability check. It is **not** a browser automation
test, not a Socket.IO integration test, and not evidence of real IPv6 traffic
detection. The simulator still performs no packet capture, no packet sending,
and no real network scanning.
