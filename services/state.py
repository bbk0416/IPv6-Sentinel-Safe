"""State models used by the IPv6 Sentinel Safe simulator."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class MonitoringStats:
    """Aggregated metrics displayed in the dashboard.

    The numbers describe locally generated sample observations only. They are not
    derived from host packet capture, network scanning, or packet transmission.
    """

    total_events: int = 0
    dhcpv6_observations: int = 0
    dns_observations: int = 0
    nd_observations: int = 0
    suspicious_events: int = 0
    policy_response_events: int = 0
    active_assets: int = 0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    network_total_mb: float = 0.0
    start_time: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, float | int]:
        uptime = time.time() - self.start_time
        safety_score = max(0, 100 - min(100, self.suspicious_events * 3 + self.policy_response_events))
        return {
            "total_events": self.total_events,
            "dhcpv6_observations": self.dhcpv6_observations,
            "dns_observations": self.dns_observations,
            "nd_observations": self.nd_observations,
            "suspicious_events": self.suspicious_events,
            "policy_response_events": self.policy_response_events,
            "active_assets": self.active_assets,
            "memory_usage": round(self.memory_usage, 1),
            "cpu_usage": round(self.cpu_usage, 1),
            "network_total_mb": round(self.network_total_mb, 2),
            "uptime": round(uptime, 1),
            "safety_score": safety_score,
        }
