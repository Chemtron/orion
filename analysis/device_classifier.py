import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DeviceClassifier:
    """
    Classifies devices as: static | transient | mobile | baseline
    Based on scan history and persistence patterns.
    """
    STATIC_MIN_SCANS = 5
    TRANSIENT_MAX_SCANS = 2
    MOBILE_RSSI_VARIANCE_THRESHOLD = 20

    def __init__(self, db):
        self.db = db

    def classify(self, mac: str, device_type: str, current_data: dict) -> str:
        device = self.db.get_device(mac, device_type)
        if not device:
            return 'new'

        scan_count = device.get('scan_count', 1)
        if device.get('is_baseline'):
            return 'baseline'
        if scan_count >= self.STATIC_MIN_SCANS:
            if self._is_mobile(mac):
                return 'mobile'
            return 'static'
        if scan_count <= self.TRANSIENT_MAX_SCANS:
            return 'transient'
        return 'recurring'

    def _is_mobile(self, mac: str) -> bool:
        """Check RSSI variance over recent scans to detect movement."""
        with self.db.get_conn() as conn:
            rows = conn.execute("""
                SELECT rssi FROM scan_events
                WHERE device_mac=? AND rssi IS NOT NULL
                ORDER BY scan_time DESC LIMIT 10
            """, (mac,)).fetchall()
        if len(rows) < 3:
            return False
        rssi_values = [r['rssi'] for r in rows]
        variance = max(rssi_values) - min(rssi_values)
        return variance >= self.MOBILE_RSSI_VARIANCE_THRESHOLD


if __name__ == '__main__':
    print("DeviceClassifier module loaded")
