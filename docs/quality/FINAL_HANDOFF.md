# Final Handoff Gate - 27.0.0-safe

`27.0.0-safe` includes a compact final handoff gate for reviewers and maintainers who want to check the source package immediately before sharing it.

Run:

```bash
python scripts/final_handoff_check.py
```

Default behavior is intentionally small and deterministic:

1. run `scripts/run_clean_validation.py`,
2. keep validation local-only,
3. avoid leaving generated cache, log, or runtime data artifacts in the source tree.

Optional reviewer modes:

```bash
python scripts/final_handoff_check.py --with-tests
python scripts/final_handoff_check.py --plan
```

- `--with-tests` adds a focused unittest handoff subset.
- `--plan` prints the expanded release checklist, including inventory refresh and temporary ZIP validation steps, without running that expanded checklist by default.

To build and verify a release ZIP explicitly, run:

```bash
python scripts/build_release.py --output ../IPv6Sentinel_SAFE_v27_release.zip
python scripts/check_release_zip.py ../IPv6Sentinel_SAFE_v27_release.zip
```

This gate improves handoff hygiene. It does **not** prove that the project is a real IPv6 detector. The project remains a safe local simulator with no packet capture, no packet sending, and no real network scanning.
