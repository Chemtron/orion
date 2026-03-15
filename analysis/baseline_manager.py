import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BaselineManager:
    """
    Manages environmental baselines — snapshot of known-good devices
    at a location, used to detect new/anomalous devices.
    """

    def __init__(self, db):
        self.db = db

    def create_baseline(self, session_name: str, location_tag: str = None) -> dict:
        """Snapshot all current devices as the baseline."""
        devices = self.db.get_all_devices()
        macs = [d['mac'] for d in devices]

        with self.db.get_conn() as conn:
            # Deactivate previous baselines
            conn.execute("UPDATE baselines SET is_active=0")

            conn.execute("""
                INSERT INTO baselines (session_name, created_time, location_tag, device_macs, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (session_name, datetime.now(timezone.utc).isoformat(), location_tag, json.dumps(macs)))

            # Mark devices as baseline
            for mac in macs:
                conn.execute("UPDATE devices SET is_baseline=1 WHERE mac=?", (mac,))

        return {
            'session_name': session_name,
            'device_count': len(macs),
            'location_tag': location_tag
        }

    def get_active_baseline(self) -> dict:
        """Get the current active baseline."""
        with self.db.get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE is_active=1 ORDER BY created_time DESC LIMIT 1"
            ).fetchone()
            if row:
                return dict(row)
        return None

    def get_non_baseline_devices(self) -> list:
        """Get devices that are NOT in the active baseline."""
        baseline = self.get_active_baseline()
        if not baseline:
            return self.db.get_all_devices()

        baseline_macs = set(json.loads(baseline.get('device_macs', '[]')))
        all_devices = self.db.get_all_devices()
        return [d for d in all_devices if d['mac'] not in baseline_macs]

    def clear_baseline(self):
        """Remove active baseline."""
        with self.db.get_conn() as conn:
            conn.execute("UPDATE baselines SET is_active=0")
            conn.execute("UPDATE devices SET is_baseline=0")


if __name__ == '__main__':
    print("BaselineManager module loaded")
