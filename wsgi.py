"""Gunicorn entry point for the container deployment path."""

from __future__ import annotations

import atexit

from app import IPv6SentinelApp


sentinel = IPv6SentinelApp()
sentinel.start_background_runtime()
atexit.register(sentinel.shutdown)
application = sentinel.app
