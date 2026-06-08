# File Inventory Integrity Gate

`docs/release/FILE_INVENTORY.json` is a deterministic SHA-256 inventory for the
source package. It helps reviewers confirm that the files they received match
the release tree that was validated before handoff.

## What it checks

- current package version
- file list, excluding generated caches/runtime data/ZIP files
- per-file size and SHA-256 hash
- aggregate package digest derived from file hashes
- platform-stable ordering based on normalized POSIX-style relative paths

## What it does not prove

- It does not prove real IPv6 detection capability.
- It does not scan or contact the network.
- It does not replace normal code review.

## Commands

```bash
python scripts/check_file_inventory.py
python scripts/check_file_inventory.py --write  # maintainers only, before release
```

If you edit any tracked project file, refresh the inventory before packaging.
