# Security Checklist

IPv6 Sentinel Safe is a local, simulation-only dashboard. Before sharing or demoing it, check the following.

## Safe defaults

- [x] Default bind address is `127.0.0.1`.
- [x] Socket.IO CORS defaults to explicit localhost origins, not `*`.
- [x] Real packet capture is disabled.
- [x] Real packet send is disabled.
- [x] Real network scanning is disabled.
- [x] Remote bind without authentication fails closed by default.
- [x] Basic Auth can be enabled through environment variables.
- [x] API responses include defensive security headers.

## Recommended demo setting

```bash
export IPV6_SENTINEL_WEB_AUTH_ENABLED=1
export IPV6_SENTINEL_USERNAME=admin
export IPV6_SENTINEL_PASSWORD='replace-with-a-long-password'
python app.py
```

## Do not add

- Packet capture libraries for live traffic collection.
- Packet crafting/transmission features.
- Network probing or scanning against real devices.
- Default remote bind such as `0.0.0.0` without authentication.
