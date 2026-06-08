from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    manifest = json.loads((ROOT / 'project_manifest.json').read_text(encoding='utf-8'))
    report = {
        'name': manifest['name'],
        'version': manifest['version'],
        'safe_mode': manifest['safe_mode'],
        'simulation_mode': manifest['simulation_mode'],
        'real_packet_capture_enabled': manifest['real_packet_capture_enabled'],
        'real_packet_send_enabled': manifest['real_packet_send_enabled'],
        'real_network_scan_enabled': manifest['real_network_scan_enabled'],
        'recommended_demo': [
            'python app.py',
            'open http://127.0.0.1:5000',
            'click 데모 시나리오',
            'download /api/report.json',
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
