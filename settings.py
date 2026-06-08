"""IPv6 Sentinel Safe settings.

Defaults are intentionally local-only and simulation-only.
Environment values are parsed defensively so a bad .env entry does not crash import.
"""

from __future__ import annotations

import os

try:
    from dotenv import load_dotenv
except Exception:  # python-dotenv is optional until dependencies are installed.
    load_dotenv = None

if load_dotenv:
    load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int, minimum: int | None = None, maximum: int | None = None) -> int:
    raw_value = os.environ.get(name, str(default))
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def _env_csv(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


APP_NAME = "IPv6 Sentinel Safe"
APP_VERSION = "27.0.0-safe"

SAFE_MODE = True
SIMULATION_MODE = True
REAL_PACKET_CAPTURE_ENABLED = False
REAL_PACKET_SEND_ENABLED = False
REAL_NETWORK_SCAN_ENABLED = False

INTERFACE = os.environ.get("IPV6_SENTINEL_INTERFACE")
INTERFACE_NAME = os.environ.get("IPV6_SENTINEL_INTERFACE_NAME")
IPV4_ADDRESS = os.environ.get("IPV6_SENTINEL_IPV4")
IPV6_ADDRESS = os.environ.get("IPV6_SENTINEL_IPV6")
MAC_ADDRESS = os.environ.get("IPV6_SENTINEL_MAC")
LOCALDOMAIN = os.environ.get("IPV6_SENTINEL_LOCALDOMAIN", "lab.local")
RELAY_TARGET = None

FLASK_HOST = os.environ.get("IPV6_SENTINEL_HOST", "127.0.0.1").strip() or "127.0.0.1"
FLASK_PORT = _env_int("IPV6_SENTINEL_PORT", 5000, 1, 65535)
FLASK_DEBUG = _env_bool("IPV6_SENTINEL_DEBUG", False)
DEBUG_MODE = FLASK_DEBUG
ALLOW_REMOTE_BIND_WITHOUT_AUTH = _env_bool("IPV6_SENTINEL_ALLOW_INSECURE_REMOTE", False)

SOCKETIO_CORS_ALLOWED_ORIGINS = _env_csv(
    "IPV6_SENTINEL_CORS",
    "http://127.0.0.1:5000,http://localhost:5000",
)
SOCKETIO_ASYNC_MODE = "threading"
SOCKETIO_PING_TIMEOUT = _env_int("IPV6_SENTINEL_SOCKETIO_PING_TIMEOUT", 60, 5, 300)
SOCKETIO_PING_INTERVAL = _env_int("IPV6_SENTINEL_SOCKETIO_PING_INTERVAL", 25, 5, 120)

WEB_AUTH_ENABLED = _env_bool("IPV6_SENTINEL_WEB_AUTH_ENABLED", False)
WEB_AUTH_USERNAME = os.environ.get("IPV6_SENTINEL_USERNAME", "admin")
WEB_AUTH_PASSWORD = os.environ.get("IPV6_SENTINEL_PASSWORD", "")

LOG_LEVEL = os.environ.get("IPV6_SENTINEL_LOG_LEVEL", "INFO")
LOG_CONSOLE_ENABLED = _env_bool("IPV6_SENTINEL_LOG_CONSOLE_ENABLED", True)
LOG_FILE_ENABLED = _env_bool("IPV6_SENTINEL_LOG_FILE_ENABLED", True)
LOG_DIR = os.environ.get("IPV6_SENTINEL_LOG_DIR", "logs")
LOG_FILE_MAX_SIZE = 5 * 1024 * 1024
LOG_FILE_BACKUP_COUNT = 3

UPDATE_INTERVAL = _env_int("IPV6_SENTINEL_UPDATE_INTERVAL", 3, 1, 60)
OBSERVATION_DB_FILE = "observations.json"
BACKUP_DIR = "backup"
