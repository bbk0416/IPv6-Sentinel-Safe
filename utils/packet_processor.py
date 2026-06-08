"""Safe observation-only packet processor stub.

Kept only for compatibility with earlier imports. It never creates, captures,
or transmits network traffic.
"""

from __future__ import annotations

from typing import Any, Dict


class PacketProcessor:
    """Observation-only helper."""

    def __init__(self, config: Any = None, security_manager: Any = None) -> None:
        self.config = config
        self.security_manager = security_manager

    def observe_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {"observed": True, "safe_mode": True, "metadata": metadata}

    def create_response(self, *_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("Response generation is disabled in safe simulation mode.")
