# Release Artifact Gate - 27.0.0-safe

`27.0.0-safe` adds a release artifact hygiene gate. It checks that the source package looks like a clean portfolio handoff before it is uploaded or shared.

The gate checks:

- required release files are present,
- runtime artifacts such as `__pycache__`, `data`, `logs`, `.pyc`, `.log`, and database files are not packaged,
- local reviewer workspaces such as `.venv/` are ignored during source-tree checks but still excluded from built ZIP files,
- the current release note is present and declared once in `project_manifest.json`,
- run scripts exist and point to the local Flask app,
- the manifest still declares the project as safe simulation only.

Run it with:

```bash
python scripts/check_release_artifact.py
```

This is a packaging hygiene check. It does **not** prove real IPv6 detection, packet inspection, or operational monitoring capability.
