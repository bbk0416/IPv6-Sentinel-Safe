# Publication hygiene gate

`27.0.0-safe` adds a static publication hygiene gate for public handoff review.

It checks that the package does not accidentally expose obvious personal markers,
plain email addresses, private IPv4 addresses, user home paths, legacy project
names, or common credential/token patterns. It also checks that the current
release note exists and that release notes are ordered consistently in
`project_manifest.json`.

Run it with:

```bash
python scripts/check_publication_hygiene.py
```

This gate is intentionally narrow. It improves public-release cleanliness, but
it does **not** prove real IPv6 monitoring, packet capture, packet injection,
network scanning, or production detection capability.
