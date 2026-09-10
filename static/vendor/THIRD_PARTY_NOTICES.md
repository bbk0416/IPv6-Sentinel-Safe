# Vendored frontend dependencies

These files are stored locally so the IPv6 Sentinel Safe dashboard does not need a third-party CDN at runtime.

- Bootstrap 5.1.3 — MIT License
- Socket.IO client 4.7.5 — MIT License
- Chart.js 4.5.1 — MIT License
- Font Awesome Free 6.0.0 — icons: CC BY 4.0; fonts: SIL OFL 1.1; code: MIT License

Exact source URLs and SHA-256 digests are recorded in `VENDOR_MANIFEST.json`. License texts are stored in the `licenses/` directory.

Do not edit minified vendor files by hand. Refresh them with `python scripts/vendor_frontend_assets.py --write` and review the resulting manifest diff.
