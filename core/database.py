import sqlite3
import json
import os
import logging
import threading
from datetime import datetime, timezone
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._is_memory = db_path == ':memory:'
        self._shared_conn = None
        self._lock = None
        if self._is_memory:
            self._lock = threading.RLock()
            self._shared_conn = sqlite3.connect(':memory:', check_same_thread=False)
            self._shared_conn.row_factory = sqlite3.Row
            self._shared_conn.execute("PRAGMA foreign_keys=ON")
        self._init_db()

    @contextmanager
    def get_conn(self):
        if self._is_memory and self._shared_conn:
            self._lock.acquire()
            try:
                yield self._shared_conn
                self._shared_conn.commit()
            except Exception:
                logger.exception("Database error")
                self._shared_conn.rollback()
                raise
            finally:
                self._lock.release()
            return
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            logger.exception("Database error")
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        with self.get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mac TEXT NOT NULL,
                    device_type TEXT NOT NULL DEFAULT 'wifi',
                    ssid TEXT,
                    vendor TEXT,
                    vendor_detail TEXT,
                    classification TEXT DEFAULT 'unknown',
                    risk_score INTEGER DEFAULT 0,
                    risk_flags TEXT DEFAULT '[]',
                    frequency_mhz INTEGER,
                    security TEXT,
                    hidden INTEGER DEFAULT 0,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    scan_count INTEGER DEFAULT 1,
                    is_baseline INTEGER DEFAULT 0,
                    enriched INTEGER DEFAULT 0,
                    enrichment_data TEXT DEFAULT '{}',
                    notes TEXT,
                    UNIQUE(mac, device_type)
                );

                CREATE TABLE IF NOT EXISTS scan_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_time TEXT NOT NULL,
                    scan_type TEXT NOT NULL,
                    device_mac TEXT NOT NULL,
                    ssid TEXT,
                    rssi INTEGER,
                    frequency_mhz INTEGER,
                    security TEXT,
                    raw_data TEXT DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS intel_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_time TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT DEFAULT 'info',
                    device_mac TEXT,
                    ssid TEXT,
                    title TEXT NOT NULL,
                    detail TEXT,
                    acknowledged INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    created_time TEXT NOT NULL,
                    location_tag TEXT,
                    device_macs TEXT DEFAULT '[]',
                    is_active INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS debriefs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_time TEXT NOT NULL,
                    window_minutes INTEGER DEFAULT 5,
                    content TEXT NOT NULL,
                    device_count INTEGER,
                    alert_count INTEGER
                );

                CREATE INDEX IF NOT EXISTS idx_scan_events_time ON scan_events(scan_time);
                CREATE INDEX IF NOT EXISTS idx_scan_events_mac ON scan_events(device_mac);
                CREATE INDEX IF NOT EXISTS idx_intel_events_time ON intel_events(event_time);
                CREATE INDEX IF NOT EXISTS idx_devices_mac ON devices(mac);
            """)

    def upsert_device(self, mac: str, device_type: str, data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        with self.get_conn() as conn:
            existing = conn.execute(
                "SELECT * FROM devices WHERE mac=? AND device_type=?", (mac, device_type)
            ).fetchone()
            if existing:
                conn.execute("""
                    UPDATE devices SET
                        ssid=COALESCE(?, ssid),
                        vendor=COALESCE(?, vendor),
                        risk_score=?,
                        risk_flags=?,
                        last_seen=?,
                        scan_count=scan_count+1,
                        classification=?,
                        frequency_mhz=COALESCE(?, frequency_mhz),
                        security=COALESCE(?, security),
                        hidden=COALESCE(?, hidden)
                    WHERE mac=? AND device_type=?
                """, (
                    data.get('ssid'), data.get('vendor'),
                    data.get('risk_score', 0),
                    json.dumps(data.get('risk_flags', [])),
                    now, data.get('classification', 'unknown'),
                    data.get('frequency_mhz'), data.get('security'),
                    data.get('hidden', 0), mac, device_type
                ))
            else:
                conn.execute("""
                    INSERT INTO devices
                    (mac, device_type, ssid, vendor, classification, risk_score,
                     risk_flags, frequency_mhz, security, hidden, first_seen, last_seen)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    mac, device_type, data.get('ssid'), data.get('vendor'),
                    data.get('classification', 'unknown'),
                    data.get('risk_score', 0),
                    json.dumps(data.get('risk_flags', [])),
                    data.get('frequency_mhz'), data.get('security'),
                    data.get('hidden', 0), now, now
                ))
        return self.get_device(mac, device_type)

    def log_scan_event(self, scan_type: str, device_mac: str, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        with self.get_conn() as conn:
            conn.execute("""
                INSERT INTO scan_events
                (scan_time, scan_type, device_mac, ssid, rssi, frequency_mhz, security, raw_data)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                now, scan_type, device_mac,
                data.get('ssid'), data.get('rssi'),
                data.get('frequency_mhz'), data.get('security'),
                json.dumps(data)
            ))

    def log_intel_event(self, event_type: str, severity: str, title: str,
                        device_mac: str = None, ssid: str = None, detail: str = None):
        now = datetime.now(timezone.utc).isoformat()
        with self.get_conn() as conn:
            conn.execute("""
                INSERT INTO intel_events
                (event_time, event_type, severity, device_mac, ssid, title, detail)
                VALUES (?,?,?,?,?,?,?)
            """, (now, event_type, severity, device_mac, ssid, title, detail))

    def get_device(self, mac: str, device_type: str) -> dict:
        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM devices WHERE mac=? AND device_type=?", (mac, device_type)
            ).fetchone()
            return dict(row) if row else None

    def get_all_devices(self, device_type: str = None, limit: int = 500) -> list:
        with self.get_conn() as conn:
            if device_type:
                rows = conn.execute(
                    "SELECT * FROM devices WHERE device_type=? ORDER BY last_seen DESC LIMIT ?",
                    (device_type, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM devices ORDER BY last_seen DESC LIMIT ?", (limit,)
                ).fetchall()
            return [dict(r) for r in rows]

    def get_intel_events(self, limit: int = 100, unacked_only: bool = False) -> list:
        with self.get_conn() as conn:
            if unacked_only:
                rows = conn.execute(
                    "SELECT * FROM intel_events WHERE acknowledged=0 ORDER BY event_time DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM intel_events ORDER BY event_time DESC LIMIT ?", (limit,)
                ).fetchall()
            return [dict(r) for r in rows]

    def cleanup_old_data(self, days: int = 7):
        """Remove scan events older than N days to prevent unbounded growth."""
        if days <= 0:
            return
        with self.get_conn() as conn:
            conn.execute("DELETE FROM scan_events WHERE scan_time < datetime('now', ?)", (f'-{days} days',))
            conn.execute("DELETE FROM intel_events WHERE acknowledged=1 AND event_time < datetime('now', ?)", (f'-{days} days',))
            logger.info("Cleaned up data older than %d days", days)

    def get_scan_history(self, minutes: int = 5) -> list:
        if minutes <= 0:
            raise ValueError(f"minutes must be positive, got {minutes}")
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT * FROM scan_events
                WHERE scan_time >= datetime('now', ?)
                ORDER BY scan_time ASC
            """, (f'-{minutes} minutes',)).fetchall()
            return [dict(r) for r in rows]


if __name__ == '__main__':
    db = Database(':memory:')
    print("Database initialized successfully")
