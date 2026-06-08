"""Deterministic local-only sample data for the simulator.

All addresses use documentation or link-local style sample values. Nothing in this
module instructs the host to scan, capture, transmit, or modify network traffic.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

SAMPLE_ASSETS: List[Dict[str, Any]] = [
    {
        "mac": "02:00:00:00:00:11",
        "host": "lab-client-01",
        "ipv4": "192.0.2.11",
        "ipv6": "fe80::211",
        "role": "Client",
        "risk_level": "LOW",
    },
    {
        "mac": "02:00:00:00:00:22",
        "host": "lab-client-02",
        "ipv4": "192.0.2.22",
        "ipv6": "fe80::222",
        "role": "Client",
        "risk_level": "LOW",
    },
    {
        "mac": "02:00:00:00:00:33",
        "host": "lab-printer",
        "ipv4": "192.0.2.33",
        "ipv6": "fe80::233",
        "role": "Printer",
        "risk_level": "MEDIUM",
    },
    {
        "mac": "02:00:00:00:00:44",
        "host": "lab-nas",
        "ipv4": "192.0.2.44",
        "ipv6": "fe80::244",
        "role": "Storage",
        "risk_level": "MEDIUM",
    },
    {
        "mac": "02:00:00:00:00:55",
        "host": "lab-router",
        "ipv4": "192.0.2.1",
        "ipv6": "fe80::255",
        "role": "Gateway",
        "risk_level": "HIGH",
    },
]

SAMPLE_EVENTS: List[Dict[str, str]] = [
    {
        "event_type": "dhcpv6_observed",
        "title": "DHCPv6 요청 관측",
        "severity": "info",
        "recommendation": "정상 범위의 주소 요청입니다. 반복 빈도만 확인하세요.",
    },
    {
        "event_type": "dns_observed",
        "title": "DNS 질의 관측",
        "severity": "info",
        "recommendation": "허용 도메인 정책과 질의 빈도를 비교하세요.",
    },
    {
        "event_type": "neighbor_discovery_observed",
        "title": "Neighbor Discovery 관측",
        "severity": "info",
        "recommendation": "신규 장비 출현 여부를 자산 목록과 대조하세요.",
    },
    {
        "event_type": "router_advertisement_observed",
        "title": "Router Advertisement 관측",
        "severity": "warning",
        "recommendation": "라우터 권한이 있는 장비인지 확인하세요.",
    },
    {
        "event_type": "suspicious_pattern_detected",
        "title": "비정상 반복 패턴 감지",
        "severity": "warning",
        "recommendation": "동일 자산의 짧은 시간 반복 요청을 점검하세요.",
    },
    {
        "event_type": "policy_response_simulated",
        "title": "정책 대응 시뮬레이션",
        "severity": "success",
        "recommendation": "교육용 정책 대응 예시입니다. 실제 장비에는 적용되지 않았습니다.",
    },
]

SCENARIO_PLAN: List[Tuple[str, int]] = [
    ("dhcpv6_observed", 0),
    ("dns_observed", 1),
    ("neighbor_discovery_observed", 2),
    ("router_advertisement_observed", 4),
    ("suspicious_pattern_detected", 4),
    ("policy_response_simulated", 4),
    ("dns_observed", 3),
    ("dhcpv6_observed", 2),
]

DEFAULT_UI_SETTINGS: Dict[str, Any] = {
    "interface": "Local Simulation",
    "simulation_speed": 5,
    "policy_response_enabled": True,
    "threat_detection": True,
    "event_retention": 300,
}
