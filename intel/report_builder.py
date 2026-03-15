import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ReportBuilder:
    """
    Generates exportable reports in JSON and text formats.
    """

    def __init__(self, db):
        self.db = db

    def build_json_report(self, window_minutes: int = 60) -> dict:
        """Build a full JSON report of the signal environment."""
        devices = self.db.get_all_devices()
        events = self.db.get_intel_events(limit=500)
        history = self.db.get_scan_history(window_minutes)

        return {
            'report_generated': datetime.now(timezone.utc).isoformat(),
            'window_minutes': window_minutes,
            'device_count': len(devices),
            'event_count': len(events),
            'devices': devices,
            'intel_events': events,
            'scan_history_count': len(history)
        }

    def build_text_report(self, window_minutes: int = 60) -> str:
        """Build a human-readable text report."""
        data = self.build_json_report(window_minutes)
        lines = [
            "=" * 60,
            "ORION SIGNAL INTELLIGENCE REPORT",
            f"Generated: {data['report_generated']}",
            f"Window: {window_minutes} minutes",
            "=" * 60,
            "",
            f"Total Devices: {data['device_count']}",
            f"Intel Events: {data['event_count']}",
            "",
            "--- HIGH RISK DEVICES ---",
        ]

        high_risk = [d for d in data['devices'] if d.get('risk_score', 0) >= 60]
        for d in sorted(high_risk, key=lambda x: x.get('risk_score', 0), reverse=True)[:20]:
            lines.append(
                f"  [{d['risk_score']:3d}] {d['mac']} | {d.get('ssid', 'N/A'):20s} | "
                f"{d.get('vendor', 'Unknown'):20s} | {d['device_type']}"
            )

        lines.append("")
        lines.append("--- RECENT ALERTS ---")
        for e in data['intel_events'][:20]:
            lines.append(f"  [{e['severity']:8s}] {e['title']} ({e['event_time'][:19]})")

        lines.append("")
        lines.append("=" * 60)
        return '\n'.join(lines)


if __name__ == '__main__':
    print("ReportBuilder module loaded")
