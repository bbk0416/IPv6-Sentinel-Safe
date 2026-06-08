"""Data-contract schemas for the safe simulator API.

The schemas are intentionally lightweight JSON-Schema-like dictionaries. They are
used for reviewer-facing documentation and for source-package validation without
adding an external jsonschema dependency.
"""

from __future__ import annotations

from typing import Any

SCHEMA_CONTRACT_VERSION = "27.0.0-safe"

SCHEMAS: dict[str, dict[str, Any]] = {
    "stats": {
        "type": "object",
        "required": [
            "total_events",
            "dhcpv6_observations",
            "dns_observations",
            "nd_observations",
            "suspicious_events",
            "policy_response_events",
            "active_assets",
            "memory_usage",
            "cpu_usage",
            "network_total_mb",
            "uptime",
            "safety_score",
        ],
        "properties": {
            "total_events": {"type": "integer", "minimum": 0},
            "dhcpv6_observations": {"type": "integer", "minimum": 0},
            "dns_observations": {"type": "integer", "minimum": 0},
            "nd_observations": {"type": "integer", "minimum": 0},
            "suspicious_events": {"type": "integer", "minimum": 0},
            "policy_response_events": {"type": "integer", "minimum": 0},
            "active_assets": {"type": "integer", "minimum": 0},
            "memory_usage": {"type": "number", "minimum": 0, "maximum": 100},
            "cpu_usage": {"type": "number", "minimum": 0, "maximum": 100},
            "network_total_mb": {"type": "number", "minimum": 0},
            "uptime": {"type": "number", "minimum": 0},
            "safety_score": {"type": "integer", "minimum": 0, "maximum": 100},
        },
    },
    "asset": {
        "type": "object",
        "required": ["asset_id", "mac", "host", "ipv4", "ipv6", "status", "first_seen", "last_seen", "observation_count", "metadata"],
        "properties": {
            "asset_id": {"type": "string", "minLength": 1},
            "mac": {"type": "string", "minLength": 1},
            "host": {"type": "string", "minLength": 1},
            "ipv4": {"type": "string"},
            "ipv6": {"type": "string"},
            "status": {"type": "string"},
            "first_seen": {"type": "string"},
            "last_seen": {"type": "string"},
            "observation_count": {"type": "integer", "minimum": 0},
            "metadata": {"type": "object"},
        },
    },
    "log": {
        "type": "object",
        "required": ["timestamp", "event_type", "asset", "status", "message", "details"],
        "properties": {
            "timestamp": {"type": "string"},
            "event_type": {"type": "string", "minLength": 1},
            "asset": {"type": "string", "minLength": 1},
            "status": {"type": "string", "enum": ["info", "success", "warning", "critical"]},
            "message": {"type": "string", "minLength": 1},
            "details": {"type": "object"},
        },
    },
    "settings": {
        "type": "object",
        "required": ["interface", "event_retention", "simulation_speed", "policy_response_enabled", "threat_detection"],
        "properties": {
            "interface": {"type": "string", "minLength": 1},
            "event_retention": {"type": "integer", "minimum": 50, "maximum": 1000},
            "simulation_speed": {"type": "integer", "minimum": 1, "maximum": 10},
            "policy_response_enabled": {"type": "boolean"},
            "threat_detection": {"type": "boolean"},
        },
    },
}


def _type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    return type(value).__name__


def validate_payload(schema_name: str, payload: dict[str, Any]) -> list[str]:
    """Return schema validation errors for a single payload.

    This deliberately implements only the small subset of JSON Schema used by
    this project so validation remains dependency-free in review environments.
    """
    schema = SCHEMAS.get(schema_name)
    if not schema:
        return [f"unknown schema: {schema_name}"]
    errors: list[str] = []
    for key in schema.get("required", []):
        if key not in payload:
            errors.append(f"{schema_name}.{key}: missing required field")
    properties = schema.get("properties", {})
    for key, rules in properties.items():
        if key not in payload:
            continue
        value = payload[key]
        actual = _type_name(value)
        expected = rules.get("type")
        if expected == "number" and actual in {"integer", "number"}:
            pass
        elif expected and actual != expected:
            errors.append(f"{schema_name}.{key}: expected {expected}, got {actual}")
            continue
        if "minimum" in rules and isinstance(value, (int, float)) and value < rules["minimum"]:
            errors.append(f"{schema_name}.{key}: below minimum {rules['minimum']}")
        if "maximum" in rules and isinstance(value, (int, float)) and value > rules["maximum"]:
            errors.append(f"{schema_name}.{key}: above maximum {rules['maximum']}")
        if "minLength" in rules and isinstance(value, str) and len(value) < rules["minLength"]:
            errors.append(f"{schema_name}.{key}: shorter than minLength {rules['minLength']}")
        if "enum" in rules and value not in rules["enum"]:
            errors.append(f"{schema_name}.{key}: not one of {rules['enum']}")
    return errors


def schema_contract_payload() -> dict[str, Any]:
    return {
        "status": "pass",
        "version": SCHEMA_CONTRACT_VERSION,
        "mode": "safe_simulation",
        "schema_count": len(SCHEMAS),
        "schemas": SCHEMAS,
        "note": "Schemas describe local simulator API payloads only; they do not claim real network detection capability.",
    }
