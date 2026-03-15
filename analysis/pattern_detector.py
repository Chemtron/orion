import logging
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger(__name__)


class PatternDetector:
    """
    Detects behavioral patterns in device scan history.
    Identifies following, co-location, intermittent, and schedule patterns.
    """

    def __init__(self, db):
        self.db = db

    def detect_following(self, target_mac: str, window_minutes: int = 30) -> list:
        """Find devices that consistently appear alongside the target device."""
        with self.db.get_conn() as conn:
            # Get target scan times
            target_scans = conn.execute("""
                SELECT scan_time FROM scan_events
                WHERE device_mac=?
                ORDER BY scan_time DESC LIMIT 50
            """, (target_mac,)).fetchall()

            if len(target_scans) < 3:
                return []

            # Single query: find all devices that appeared within window_minutes of any target scan
            rows = conn.execute("""
                SELECT se.device_mac, COUNT(DISTINCT ts.scan_time) as co_count
                FROM scan_events se
                INNER JOIN (SELECT DISTINCT scan_time FROM scan_events WHERE device_mac=? ORDER BY scan_time DESC LIMIT 50) ts
                ON se.scan_time BETWEEN datetime(ts.scan_time, '-' || ? || ' minutes') AND datetime(ts.scan_time, '+' || ? || ' minutes')
                WHERE se.device_mac != ?
                GROUP BY se.device_mac
            """, (target_mac, str(window_minutes), str(window_minutes), target_mac)).fetchall()

        total_scans = len(target_scans)
        threshold = total_scans * 0.6
        followers = [
            {'mac': r['device_mac'], 'co_occurrences': r['co_count'], 'correlation': round(r['co_count'] / total_scans, 2)}
            for r in rows
            if r['co_count'] >= threshold
        ]
        return sorted(followers, key=lambda x: x['correlation'], reverse=True)

    def detect_schedule(self, mac: str) -> dict:
        """Detect if a device appears on a regular schedule."""
        with self.db.get_conn() as conn:
            rows = conn.execute("""
                SELECT scan_time FROM scan_events
                WHERE device_mac=?
                ORDER BY scan_time ASC
            """, (mac,)).fetchall()

        if len(rows) < 5:
            return {'has_schedule': False}

        hours = []
        for r in rows:
            try:
                hours.append(datetime.fromisoformat(r['scan_time']).hour)
            except (ValueError, TypeError) as e:
                logger.warning("Failed to parse scan_time '%s': %s", r['scan_time'], e)
                continue

        if not hours:
            return {'has_schedule': False}

        hour_counts = Counter(hours)
        peak_hour = hour_counts.most_common(1)[0]

        return {
            'has_schedule': peak_hour[1] >= len(rows) * 0.4,
            'peak_hour': peak_hour[0],
            'peak_count': peak_hour[1],
            'total_scans': len(rows),
            'hour_distribution': dict(hour_counts)
        }

    def detect_intermittent(self, mac: str) -> dict:
        """Detect devices that appear and disappear regularly (potential tracking device)."""
        with self.db.get_conn() as conn:
            rows = conn.execute("""
                SELECT scan_time FROM scan_events
                WHERE device_mac=?
                ORDER BY scan_time ASC
            """, (mac,)).fetchall()

        if len(rows) < 4:
            return {'is_intermittent': False}

        times = [datetime.fromisoformat(r['scan_time']) for r in rows]
        gaps = [(times[i+1] - times[i]).total_seconds() for i in range(len(times)-1)]

        if not gaps:
            return {'is_intermittent': False}

        avg_gap = sum(gaps) / len(gaps)
        return {
            'is_intermittent': any(g > avg_gap * 3 for g in gaps),
            'avg_gap_seconds': round(avg_gap),
            'max_gap_seconds': round(max(gaps)),
            'appearances': len(rows)
        }


if __name__ == '__main__':
    print("PatternDetector module loaded")
