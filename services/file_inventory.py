"""Release file inventory and integrity checks.

This module builds a deterministic SHA-256 inventory for reviewer-facing source
packages. It is intentionally local and read-only: it hashes files in the
project tree, ignores generated caches/runtime data, and never contacts a
network or modifies the host.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CURRENT_VERSION = "27.0.0-safe"
INVENTORY_PATH = Path("docs/release/FILE_INVENTORY.json")

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "venv",
    ".testvenv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "logs",
    "data",
    "backup",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".log", ".db", ".sqlite", ".zip"}


@dataclass(frozen=True)
class InventoryComparison:
    name: str
    ok: bool
    detail: Any

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if rel == INVENTORY_PATH:
        return False
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()



def _inventory_sort_key(path: Path, root: Path) -> str:
    """Return a platform-stable inventory sort key.

    ``Path`` ordering is OS-specific: WindowsPath and PosixPath can order the
    same extracted tree differently, which changes the package digest even when
    every file hash is identical.  Always sort by normalized POSIX-style
    relative path so Linux, macOS, and Windows produce the same inventory.
    """
    return path.relative_to(root).as_posix()


def iter_candidate_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in EXCLUDED_PARTS)
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            if should_include(path, root):
                files.append(path)
    return sorted(files, key=lambda path: _inventory_sort_key(path, root))

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_file_inventory(root: Path, *, version: str = CURRENT_VERSION) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in iter_candidate_files(root):
        rel = path.relative_to(root).as_posix()
        files.append({"path": rel, "size": path.stat().st_size, "sha256": sha256_file(path)})
    package_digest = hashlib.sha256(
        "\n".join(f"{item['sha256']}  {item['path']}" for item in files).encode("utf-8")
    ).hexdigest()
    return {
        "schema_version": 1,
        "version": version,
        "mode": "safe_simulation",
        "generated_by": "scripts/check_file_inventory.py --write",
        "note": "Deterministic file inventory excluding generated caches, runtime data, ZIP files, and this inventory file.",
        "file_count": len(files),
        "package_sha256": package_digest,
        "files": files,
    }


def load_expected_inventory(root: Path) -> dict[str, Any]:
    try:
        return json.loads((root / INVENTORY_PATH).read_text(encoding="utf-8"))
    except Exception:
        return {}


def run_file_inventory_check(*, app_root: Path, app_version: str) -> dict[str, Any]:
    expected = load_expected_inventory(app_root)
    actual = build_file_inventory(app_root, version=app_version)

    expected_files = {item.get("path"): item for item in expected.get("files", []) if isinstance(item, dict)}
    actual_files = {item.get("path"): item for item in actual.get("files", []) if isinstance(item, dict)}

    missing = sorted(set(expected_files) - set(actual_files))
    extra = sorted(set(actual_files) - set(expected_files))
    changed = sorted(
        path
        for path in set(expected_files) & set(actual_files)
        if expected_files[path].get("sha256") != actual_files[path].get("sha256")
        or expected_files[path].get("size") != actual_files[path].get("size")
    )

    checks = [
        InventoryComparison(
            "inventory_file_present",
            bool(expected),
            str(INVENTORY_PATH) if expected else "inventory file missing or unreadable",
        ),
        InventoryComparison(
            "inventory_version_matches_app",
            expected.get("version") == app_version,
            {"expected_inventory_version": expected.get("version"), "app_version": app_version},
        ),
        InventoryComparison(
            "inventory_file_set_matches_workspace",
            not missing and not extra,
            {"missing": missing[:50], "extra": extra[:50], "missing_count": len(missing), "extra_count": len(extra)},
        ),
        InventoryComparison(
            "inventory_hashes_match_workspace",
            not changed,
            {"changed": changed[:50], "changed_count": len(changed)},
        ),
        InventoryComparison(
            "package_digest_matches_workspace",
            expected.get("package_sha256") == actual.get("package_sha256"),
            {"expected": expected.get("package_sha256"), "actual": actual.get("package_sha256")},
        ),
    ]
    items = [check.to_dict() for check in checks]
    failures = [item for item in items if not item["ok"]]
    return {
        "status": "pass" if not failures else "fail",
        "version": app_version,
        "mode": "safe_simulation",
        "summary": {"total": len(items), "passed": len(items) - len(failures), "failures": len(failures)},
        "checks": items,
        "inventory": {
            "file_count": actual["file_count"],
            "package_sha256": actual["package_sha256"],
            "inventory_path": str(INVENTORY_PATH),
        },
    }
