# Manifest Hygiene Gate

`project_manifest.json` is the compact map reviewers use to understand this package.
The manifest hygiene gate keeps that map from drifting away from the source tree.

## What it checks

- The manifest version matches the current safe release.
- List-style manifest fields do not contain duplicate entries.
- `included_final_docs` entries exist on disk.
- Reviewer export endpoints are also declared in `api_endpoints`.
- `release_notes` matches the actual `RELEASE_NOTES_v*.md` files in the package.
- The current release note is present exactly once.
- The manifest still states the simulation-only safety boundary.

## What it does not check

- It does not prove real IPv6 traffic detection.
- It does not start the Flask server.
- It does not open sockets, capture packets, scan networks, or transmit packets.
- It does not replace API contract, schema contract, or runtime tests.

## CLI

```bash
python scripts/check_manifest_hygiene.py
```

## API

```bash
curl http://127.0.0.1:5000/api/manifest
```
