"""Runtime diagnostics for the local-only simulator."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

BLOCKED_IMPORTS = {"scapy", "mitmproxy", "wmi"}
BLOCKED_TOKENS = {"start_attack", "stop_attack", "set_attack_intensity", "attack_status", "attack_logs", "attack_intensity"}


@dataclass(frozen=True)
class DiagnosticResult:
    name: str
    ok: bool
    detail: str

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


def summarize_diagnostics(results: Iterable[DiagnosticResult]) -> Dict[str, Any]:
    items = [result.to_dict() for result in results]
    return {
        "status": "pass" if all(item["ok"] for item in items) else "fail",
        "checks": items,
    }


def runtime_diagnostics(
    *,
    safe_mode: bool,
    simulation_mode: bool,
    packet_flags: Mapping[str, bool],
    auth_enabled: bool,
    local_or_auth_protected: bool,
    app_root: Path,
) -> Dict[str, Any]:
    """Return a reviewer-friendly diagnostic payload.

    This does not inspect or touch the network. It only reviews app flags and
    source text for obvious unsafe dependencies/tokens.
    """
    results = [
        DiagnosticResult("safe_mode_enabled", bool(safe_mode), "SAFE_MODE must remain true."),
        DiagnosticResult("simulation_mode_enabled", bool(simulation_mode), "SIMULATION_MODE must remain true."),
        DiagnosticResult(
            "real_packet_features_disabled",
            not any(packet_flags.values()),
            f"packet flags: {dict(packet_flags)}",
        ),
        DiagnosticResult(
            "local_or_auth_protected",
            bool(local_or_auth_protected),
            "Remote binding must require authentication.",
        ),
        DiagnosticResult("auth_flag_reported", isinstance(auth_enabled, bool), f"auth_enabled={auth_enabled}"),
    ]
    results.extend(static_source_diagnostics(app_root))
    return summarize_diagnostics(results)


def static_source_diagnostics(app_root: Path) -> list[DiagnosticResult]:
    skip_parts = {".venv", "venv", "env", ".testvenv", "node_modules", "__pycache__", "tests", "scripts"}
    text_files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(app_root):
        dirnames[:] = [name for name in dirnames if name not in skip_parts]
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            if filename.endswith(".py") and path.name != "diagnostics.py":
                text_files.append(path)
    joined = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in text_files)


    blocked_import_hits = [token for token in sorted(BLOCKED_IMPORTS) if f"import {token}" in joined or f"from {token}" in joined]
    blocked_token_hits = [token for token in sorted(BLOCKED_TOKENS) if token in joined]

    return [
        DiagnosticResult(
            "no_blocked_network_imports",
            not blocked_import_hits,
            "blocked imports found: " + ", ".join(blocked_import_hits) if blocked_import_hits else "none",
        ),
        DiagnosticResult(
            "no_legacy_attack_tokens",
            not blocked_token_hits,
            "legacy tokens found: " + ", ".join(blocked_token_hits) if blocked_token_hits else "none",
        ),
    ]
