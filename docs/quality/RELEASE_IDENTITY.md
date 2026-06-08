# Release Identity Gate - 27.0.0-safe

`27.0.0-safe` adds a static release identity gate. It checks that the current safe version is aligned across:

- `settings.py`
- `pyproject.toml`
- `project_manifest.json`
- `docs/api/openapi.yaml`
- README / validation / completion / release handoff documents
- `manifest.release_notes` uniqueness

This gate does not prove real IPv6 detection capability. It only prevents stale release metadata from making the package look more consistent than it is.

Run it with:

```bash
python scripts/check_release_identity.py
```
