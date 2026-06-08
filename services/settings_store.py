"""Validated dashboard settings persistence for IPv6 Sentinel Safe.

The store accepts only a small allow-list of UI preferences. Unknown keys are
ignored and known keys are clamped, so malformed browser/API payloads cannot
turn the simulator into an unsafe or noisy process.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from services.simulation_catalog import DEFAULT_UI_SETTINGS


def bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    """Parse an integer and clamp it into a safe range."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def bounded_text(value: Any, default: str, max_length: int = 80) -> str:
    """Normalize short UI text without allowing giant payloads."""
    text = str(value).strip() if value is not None else default
    return (text or default)[:max_length]


def bounded_bool(value: Any, default: bool) -> bool:
    """Parse common boolean forms while preserving a safe default."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    if value in {0, 1}:
        return bool(value)
    return default


def normalize_settings(payload: Dict[str, Any] | None, current: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Merge and validate dashboard settings.

    Only keys from DEFAULT_UI_SETTINGS are returned. This makes settings exports
    deterministic and prevents stale/unknown UI flags from accumulating.
    """
    allowed = dict(DEFAULT_UI_SETTINGS)
    updated = dict(allowed)
    if current:
        updated.update({key: current[key] for key in allowed.keys() & current.keys()})
    payload = payload or {}

    if "interface" in payload:
        updated["interface"] = bounded_text(payload.get("interface"), str(updated["interface"]))
    if "simulation_speed" in payload:
        updated["simulation_speed"] = bounded_int(
            payload.get("simulation_speed"), int(updated.get("simulation_speed", 5)), 1, 10
        )
    if "policy_response_enabled" in payload:
        updated["policy_response_enabled"] = bounded_bool(payload.get("policy_response_enabled"), bool(updated.get("policy_response_enabled", True)))
    if "threat_detection" in payload:
        updated["threat_detection"] = bounded_bool(
            payload.get("threat_detection"), bool(updated.get("threat_detection", True))
        )
    if "event_retention" in payload:
        updated["event_retention"] = bounded_int(
            payload.get("event_retention"), int(updated.get("event_retention", 300)), 50, 1000
        )

    return {key: updated.get(key, value) for key, value in allowed.items()}


class SettingsStore:
    """Small file-backed store for local dashboard preferences."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return normalize_settings({})
        try:
            saved = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return normalize_settings({})
        if not isinstance(saved, dict):
            return normalize_settings({})
        return normalize_settings(saved)

    def save(self, payload: Dict[str, Any], current: Dict[str, Any] | None = None) -> Dict[str, Any]:
        settings = normalize_settings(payload, current)
        self.path.parent.mkdir(exist_ok=True)
        self.path.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
        return dict(settings)
