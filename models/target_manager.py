"""Observed asset model for the safe dashboard."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Target:
    """Dashboard asset observed in local simulation data."""

    mac: str
    host: str
    ipv4: Optional[str] = ""
    ipv6: Optional[str] = ""
    status: str = "observed"
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    observation_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def asset_id(self) -> str:
        return self.mac.replace(":", "").lower()

    def update_last_seen(self) -> None:
        self.last_seen = time.time()
        self.observation_count += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "mac": self.mac,
            "host": self.host,
            "ipv4": self.ipv4 or "",
            "ipv6": self.ipv6 or "",
            "status": self.status,
            "first_seen": datetime.fromtimestamp(self.first_seen).isoformat(timespec="seconds"),
            "last_seen": datetime.fromtimestamp(self.last_seen).isoformat(timespec="seconds"),
            "observation_count": self.observation_count,
            "metadata": self.metadata,
        }
