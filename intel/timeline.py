import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Timeline:
    """
    Intel Timeline log manager.
    Provides filtered views of intel events.
    """

    def __init__(self, db):
        self.db = db

    def get_events(self, limit: int = 100, severity: str = None,
                   event_type: str = None, unacked_only: bool = False) -> list:
        """Get filtered intel events."""
        # Cap limit at 1000
        if limit > 1000:
            limit = 1000

        with self.db.get_conn() as conn:
            query = "SELECT * FROM intel_events WHERE 1=1"
            params = []

            if severity:
                query += " AND severity=?"
                params.append(severity)

            if event_type:
                query += " AND event_type=?"
                params.append(event_type)

            if unacked_only:
                query += " AND acknowledged=0"

            query += " ORDER BY event_time DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def acknowledge_event(self, event_id: int):
        with self.db.get_conn() as conn:
            conn.execute("UPDATE intel_events SET acknowledged=1 WHERE id=?", (event_id,))

    def acknowledge_all(self):
        with self.db.get_conn() as conn:
            conn.execute("UPDATE intel_events SET acknowledged=1 WHERE acknowledged=0")

    def get_severity_counts(self) -> dict:
        """Get count of unacknowledged events by severity."""
        with self.db.get_conn() as conn:
            rows = conn.execute("""
                SELECT severity, COUNT(*) as count
                FROM intel_events WHERE acknowledged=0
                GROUP BY severity
            """).fetchall()
            return {r['severity']: r['count'] for r in rows}

    def clear_old_events(self, days: int = 30):
        """Remove events older than N days."""
        if days <= 0:
            logger.warning("Invalid days parameter %d — must be > 0", days)
            return
        with self.db.get_conn() as conn:
            conn.execute("""
                DELETE FROM intel_events
                WHERE event_time < datetime('now', ?)
            """, (f'-{days} days',))


if __name__ == '__main__':
    print("Timeline module loaded")
