# Release ZIP Gate - 27.0.0-safe

`27.0.0-safe` adds a release ZIP validator for the portfolio handoff archive.

The validator checks that a built ZIP:

- has exactly one top-level project directory;
- includes the current release note and reviewer handoff files;
- excludes Python caches, test caches, runtime logs, runtime data, virtual environments, local databases, and nested ZIP files;
- declares `safe_mode=true` and `simulation_mode=true` in `project_manifest.json`;
- keeps the manifest version aligned with the application version.

Run it with:

```bash
python scripts/check_release_zip.py
```

To inspect a specific archive:

```bash
python scripts/check_release_zip.py ../IPv6Sentinel_SAFE_v27_release.zip
```

This is a packaging check only. It does not prove that the project is a real IPv6 traffic detector.
