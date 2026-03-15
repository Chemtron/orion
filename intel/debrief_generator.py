import json
import logging
from datetime import datetime, timezone
from collections import Counter

logger = logging.getLogger(__name__)


class DebriefGenerator:
    """
    Generates structured 5-minute environmental intelligence debriefs.
    Output is human-readable and AI-prompt-friendly.
    """

    def __init__(self, db):
        self.db = db

    def generate(self, window_minutes: int = 5) -> dict:
        history = self.db.get_scan_history(window_minutes)
        all_devices = self.db.get_all_devices()
        intel_events = self.db.get_intel_events(limit=50)

        wifi_devices = [d for d in all_devices if d['device_type'] == 'wifi']
        ble_devices = [d for d in all_devices if d['device_type'] == 'ble']
        network_devices = [d for d in all_devices if d['device_type'] == 'network']

        high_risk = [d for d in all_devices if d.get('risk_score', 0) >= 60]
        new_devices = [d for d in all_devices if d.get('classification') == 'new']
        recent_alerts = [e for e in intel_events
                        if e['severity'] in ('critical', 'high') and not e['acknowledged']]

        scan_times = sorted(set(e['scan_time'][:16] for e in history))
        density_by_minute = Counter(e['scan_time'][:16] for e in history)

        debrief = {
            'generated': datetime.now(timezone.utc).isoformat(),
            'window_minutes': window_minutes,
            'summary': {
                'total_wifi': len(wifi_devices),
                'total_ble': len(ble_devices),
                'total_network': len(network_devices),
                'high_risk_count': len(high_risk),
                'new_device_count': len(new_devices),
                'active_alerts': len(recent_alerts)
            },
            'high_risk_devices': [
                {
                    'mac': d['mac'],
                    'type': d['device_type'],
                    'ssid': d.get('ssid', ''),
                    'vendor': d.get('vendor', 'Unknown'),
                    'risk_score': d['risk_score'],
                    'flags': json.loads(d.get('risk_flags') or '[]'),
                    'classification': d.get('classification')
                }
                for d in sorted(high_risk, key=lambda x: x['risk_score'], reverse=True)[:10]
            ],
            'new_devices': [
                {'mac': d['mac'], 'type': d['device_type'], 'ssid': d.get('ssid', '')}
                for d in new_devices[:10]
            ],
            'active_alerts': [
                {'title': e['title'], 'severity': e['severity'], 'time': e['event_time']}
                for e in recent_alerts[:10]
            ],
            'signal_density': dict(density_by_minute),
            'ai_prompt': self._build_ai_prompt(window_minutes, wifi_devices, ble_devices, high_risk, recent_alerts)
        }
        return debrief

    def _build_ai_prompt(self, window, wifi, ble, high_risk, alerts) -> str:
        lines = [
            f"[ORION SIGNAL INTEL DEBRIEF — {window}-MINUTE WINDOW]",
            f"WiFi devices in range: {len(wifi)}",
            f"BLE devices in range: {len(ble)}",
            f"High-risk devices: {len(high_risk)}",
            f"Active alerts: {len(alerts)}",
            "",
            "HIGH RISK DEVICES:"
        ]
        for d in high_risk[:5]:
            lines.append(f"  - {d.get('vendor','Unknown')} | {d.get('ssid','')} | "
                        f"Score: {d['risk_score']} | Flags: {d.get('risk_flags','')}")
        if alerts:
            lines.append("\nACTIVE ALERTS:")
            for a in alerts[:5]:
                lines.append(f"  [{a['severity'].upper()}] {a['title']}")
        lines.append("\nAnalyze this signal environment and identify any concerning patterns, "
                    "potential surveillance devices, or security recommendations.")
        return '\n'.join(lines)


if __name__ == '__main__':
    print("DebriefGenerator module loaded")
