"""Public-release hygiene checks for reviewer handoff.

This module looks for common mistakes that make a portfolio ZIP awkward to
publish: personal identifiers, private network addresses, legacy project names,
obvious credential patterns, and stale current-version markers in old release
notes. It is static, read-only, and never opens sockets, captures packets, or
contacts any external service.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

CURRENT_VERSION = "27.0.0-safe"
CURRENT_RELEASE_NOTE = "RELEASE_NOTES_v27.md"
CURRENT_RELEASE_TOKEN = "v27"

TEXT_SUFFIXES = {
    "", ".bat", ".css", ".dockerignore", ".env", ".example", ".gitignore",
    ".html", ".ini", ".json", ".md", ".py", ".sh", ".svg", ".toml",
    ".txt", ".yaml", ".yml",
}
SKIP_PARTS = {".git", ".venv", "venv", "env", ".testvenv", "__pycache__", "node_modules"}
SKIP_SUFFIXES = {".png", ".ico", ".zip", ".pyc", ".pyo"}

PERSONAL_MARKERS = (
    # Keep these examples generic so the public package itself does not embed
    # an author's private handle, email domain, or local machine name.
    "your-real-name",
    "your-private-email-domain",
    "personal-handle",
    "legacy-project-name",
    "darkv6",
    "ipv6phantom",
)
SECRET_PATTERNS = {
    "aws_access_key_id": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "openai_style_token": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PRIVATE_IPV4_RE = re.compile(r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})\b")
USER_PATH_RE = re.compile(r"(?:/Users/[^\s'\"]+|/home/[^\s'\"]+|C:\\\\Users\\\\[^\s'\"]+)")


@dataclass(frozen=True)
class PublicationCheck:
    name: str
    ok: bool
    detail: Any

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


def _iter_text_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_PARTS]
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            if not path.is_file():
                continue
            if path.name == "publication_hygiene.py":
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            yield path


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _find_marker_hits(root: Path, markers: Iterable[str]) -> list[dict[str, str]]:
    lowered_markers = tuple(marker.lower() for marker in markers)
    hits: list[dict[str, str]] = []
    for path in _iter_text_files(root):
        text = _read(path)
        lowered = text.lower()
        for marker in lowered_markers:
            if marker in lowered:
                hits.append({"path": path.relative_to(root).as_posix(), "marker": marker})
    return hits


def _find_regex_hits(root: Path, patterns: dict[str, re.Pattern[str]]) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path in _iter_text_files(root):
        # Unit tests may intentionally contain dummy strings for negative checks.
        if "tests" in path.relative_to(root).parts:
            continue
        text = _read(path)
        for name, pattern in patterns.items():
            if pattern.search(text):
                hits.append({"path": path.relative_to(root).as_posix(), "pattern": name})
    return hits


def _find_email_hits(root: Path) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path in _iter_text_files(root):
        text = _read(path)
        for email in sorted(set(EMAIL_RE.findall(text))):
            hits.append({"path": path.relative_to(root).as_posix(), "email": email})
    return hits


def _find_private_ip_hits(root: Path) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path in _iter_text_files(root):
        text = _read(path)
        for ip in sorted(set(PRIVATE_IPV4_RE.findall(text))):
            hits.append({"path": path.relative_to(root).as_posix(), "ip": ip})
    return hits


def _find_user_path_hits(root: Path) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path in _iter_text_files(root):
        text = _read(path)
        for value in sorted(set(USER_PATH_RE.findall(text))):
            hits.append({"path": path.relative_to(root).as_posix(), "path_value": value})
    return hits


def _release_note_order(root: Path) -> list[str]:
    def key(path: Path) -> int:
        try:
            return int(path.stem.split("_v", 1)[1])
        except Exception:
            return -1
    return [path.name for path in sorted(root.glob("RELEASE_NOTES_v*.md"), key=key, reverse=True)]


def run_publication_hygiene_check(*, app_root: Path, app_version: str) -> dict[str, Any]:
    manifest_path = app_root / "project_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        manifest = {}

    marker_hits = _find_marker_hits(app_root, PERSONAL_MARKERS)
    secret_hits = _find_regex_hits(app_root, SECRET_PATTERNS)
    email_hits = _find_email_hits(app_root)
    private_ip_hits = _find_private_ip_hits(app_root)
    user_path_hits = _find_user_path_hits(app_root)
    release_notes = _release_note_order(app_root)
    manifest_notes = manifest.get("release_notes", []) if isinstance(manifest.get("release_notes"), list) else []
    current_note_text = _read(app_root / CURRENT_RELEASE_NOTE)

    stale_current_markers = []
    for note in app_root.glob("RELEASE_NOTES_v*.md"):
        if note.name == CURRENT_RELEASE_NOTE:
            continue
        first_line = (_read(note).splitlines() or [""])[0]
        if CURRENT_VERSION in first_line:
            stale_current_markers.append(note.name)

    checks = [
        PublicationCheck(
            "publication_version_matches_app",
            app_version == CURRENT_VERSION,
            {"app_version": app_version, "expected": CURRENT_VERSION},
        ),
        PublicationCheck(
            "current_release_note_present",
            (app_root / CURRENT_RELEASE_NOTE).exists() and CURRENT_VERSION in current_note_text,
            {"release_note": CURRENT_RELEASE_NOTE},
        ),
        PublicationCheck(
            "manifest_release_notes_are_complete_and_ordered",
            manifest_notes == release_notes,
            {"manifest_first": manifest_notes[:3], "tree_first": release_notes[:3], "manifest_count": len(manifest_notes), "tree_count": len(release_notes)},
        ),
        PublicationCheck(
            "no_personal_or_legacy_project_markers",
            not marker_hits,
            marker_hits[:20],
        ),
        PublicationCheck(
            "no_plain_email_addresses",
            not email_hits,
            email_hits[:20],
        ),
        PublicationCheck(
            "no_private_ipv4_addresses",
            not private_ip_hits,
            private_ip_hits[:20],
        ),
        PublicationCheck(
            "no_user_home_paths",
            not user_path_hits,
            user_path_hits[:20],
        ),
        PublicationCheck(
            "no_obvious_secret_patterns",
            not secret_hits,
            secret_hits[:20],
        ),
        PublicationCheck(
            "older_release_notes_do_not_claim_current_version",
            not stale_current_markers,
            stale_current_markers,
        ),
    ]
    items = [check.to_dict() for check in checks]
    failures = [item for item in items if not item["ok"]]
    return {
        "status": "pass" if not failures else "fail",
        "version": CURRENT_VERSION,
        "mode": "safe_simulation",
        "summary": {"total": len(items), "passed": len(items) - len(failures), "failures": len(failures)},
        "checks": items,
        "notes": [
            "This is a publication hygiene check only.",
            "It does not prove real IPv6 traffic detection or production security monitoring capability.",
        ],
    }
