"""Read-only performance metrics for IPv6 Sentinel Safe."""

from __future__ import annotations

import time
from typing import Dict

import psutil


class PerformanceMonitor:
    """Collect lightweight system metrics without assuming network counters exist."""

    def __init__(self) -> None:
        self.started_at = time.time()
        self._last_net_total = self._net_total_bytes()
        self._last_net_ts = time.time()

    @staticmethod
    def _net_total_bytes() -> int:
        """Return total network bytes, or 0 when the host does not expose counters."""
        try:
            counters = psutil.net_io_counters()
        except Exception:
            return 0
        if counters is None:
            return 0
        return int(getattr(counters, "bytes_sent", 0) + getattr(counters, "bytes_recv", 0))

    @staticmethod
    def _safe_percent(callable_obj, default: float = 0.0) -> float:
        try:
            value = callable_obj()
            return float(value if value is not None else default)
        except Exception:
            return default

    def snapshot(self) -> Dict[str, float | int]:
        now = time.time()
        current_total = self._net_total_bytes()
        elapsed = max(0.001, now - self._last_net_ts)
        throughput_mbps = ((current_total - self._last_net_total) * 8 / 1_000_000) / elapsed
        self._last_net_total = current_total
        self._last_net_ts = now

        try:
            memory_usage = float(psutil.virtual_memory().percent)
        except Exception:
            memory_usage = 0.0
        try:
            disk_usage = float(psutil.disk_usage("/").percent)
        except Exception:
            disk_usage = 0.0
        try:
            process_memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        except Exception:
            process_memory_mb = 0.0

        return {
            "cpu_usage": round(self._safe_percent(lambda: psutil.cpu_percent(interval=None)), 1),
            "memory_usage": round(memory_usage, 1),
            "disk_usage": round(disk_usage, 1),
            "network_throughput_mbps": round(max(0.0, throughput_mbps), 3),
            "process_memory_mb": round(process_memory_mb, 1),
            "uptime": round(now - self.started_at, 1),
        }

    def shutdown(self) -> None:
        return None
