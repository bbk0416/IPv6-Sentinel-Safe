"""Read-only local configuration helper.

No packet capture, packet transmission, or network probing is performed here.
The class only reads interface metadata already exposed by the operating system.
"""

from __future__ import annotations

import os
import socket
from typing import Dict, List, Optional

import psutil

from settings import INTERFACE, INTERFACE_NAME, IPV4_ADDRESS, IPV6_ADDRESS, LOCALDOMAIN, MAC_ADDRESS, RELAY_TARGET
from utils.logger import setup_logger


class Config:
    """Read-only local network metadata used for labels and diagnostics."""

    def __init__(self) -> None:
        self.logger = setup_logger("Config")
        self.interface = INTERFACE or self.get_active_interface()
        self.interfaceName = INTERFACE_NAME or self.interface or "loopback"
        self.v4addr = IPV4_ADDRESS or self._get_ipv4_address()
        self.v6addr = IPV6_ADDRESS or self._get_ipv6_address()
        self.macaddr = MAC_ADDRESS or self._get_mac_address()
        self.ipv6prefix = "fe80::"
        self.localdomain = LOCALDOMAIN.lower() if LOCALDOMAIN else None
        self.selfaddr = (self.v6addr or "::1").split("%")[0]
        self.selfmac = self.macaddr or "00:00:00:00:00:00"
        self.selfduid = f"SAFE-SIM-{self.selfmac}"
        self.relay = RELAY_TARGET.lower() if RELAY_TARGET and hasattr(RELAY_TARGET, "lower") else None
        self.print_config_info()

    @staticmethod
    def _interface_addresses() -> Dict[str, List[object]]:
        try:
            return psutil.net_if_addrs() or {}
        except Exception:
            return {}

    def get_active_interface(self) -> Optional[str]:
        preferred = os.environ.get("IPV6_SENTINEL_INTERFACE")
        if preferred:
            return preferred
        interfaces = self._interface_addresses()
        for interface, addrs in interfaces.items():
            if interface.lower().startswith(("lo", "loopback")):
                continue
            if any(getattr(addr, "family", None) in (socket.AF_INET, socket.AF_INET6) for addr in addrs):
                return interface
        return next(iter(interfaces), None)

    def _get_ipv4_address(self) -> Optional[str]:
        if not self.interface:
            return None
        for addr in self._interface_addresses().get(self.interface, []):
            if getattr(addr, "family", None) == socket.AF_INET:
                return getattr(addr, "address", None)
        return None

    def _get_ipv6_address(self) -> Optional[str]:
        if not self.interface:
            return None
        for addr in self._interface_addresses().get(self.interface, []):
            if getattr(addr, "family", None) == socket.AF_INET6:
                return getattr(addr, "address", None)
        return None

    def _get_mac_address(self) -> Optional[str]:
        if not self.interface:
            return None
        link_family = getattr(psutil, "AF_LINK", None)
        for addr in self._interface_addresses().get(self.interface, []):
            if getattr(addr, "family", None) == link_family:
                return getattr(addr, "address", None)
        return None

    @staticmethod
    def _mask_ipv4(value: Optional[str]) -> str:
        if not value:
            return "없음"
        parts = value.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
        return "configured"

    @staticmethod
    def _mask_ipv6(value: Optional[str]) -> str:
        if not value:
            return "없음"
        prefix = value.split("%", 1)[0].split(":")[:2]
        return ":".join(part for part in prefix if part) + "::/masked" if prefix else "configured"

    @staticmethod
    def _mask_mac(value: Optional[str]) -> str:
        if not value:
            return "없음"
        parts = value.split(":")
        if len(parts) >= 3:
            return ":".join(parts[:3]) + ":**:**:**"
        return "configured"

    def print_config_info(self) -> None:
        self.logger.info(
            "안전 모드 설정 | interface=%s ipv4=%s ipv6=%s mac=%s packet_io=disabled",
            self.interfaceName,
            self._mask_ipv4(self.v4addr),
            self._mask_ipv6(self.v6addr),
            self._mask_mac(self.macaddr),
        )
