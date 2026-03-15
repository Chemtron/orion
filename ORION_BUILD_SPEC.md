# ORION — Open Source Passive Signal Intelligence Platform
## Complete Technical Build Specification for Claude Code

**Version:** 1.0.0  
**Project Root:** `C:\Projects\orion`  
**GitHub Repo:** `https://github.com/[YOUR_HANDLE]/orion` (created in Phase 0)  
**Stack:** Python 3.11+ / Flask / SQLite / HTML + CSS + Vanilla JS / Termux:API / BlueZ  
**Platforms:** Android (Termux) + Raspberry Pi + Linux  
**License:** MIT

---

## CRITICAL RULES FOR CLAUDE

- **NO React. NO Vue. NO Angular. NO framework JS.** Vanilla HTML/CSS/JS only for all UI.
- **NO inline styles in HTML.** All styles go in `static/css/`.
- **NO hardcoded paths.** Use `os.path.join` and relative paths throughout.
- **ALL Python files must include a `if __name__ == '__main__':` guard.**
- **ALL API endpoints return JSON.** Never return HTML from `/api/*` routes.
- **SQLite only.** No PostgreSQL, MySQL, or external database dependencies.
- **Zero cloud dependencies at runtime.** All enrichment APIs are optional and user-configured.
- **Every module must have its own test file** in `tests/`.
- Do not modify files outside `C:\Projects\orion`.

---

## PHASE 0: GITHUB REPOSITORY SETUP

### 0.1 — Human Action Required: Create GitHub Repository

Claude cannot create a GitHub repository directly. The human must complete this step manually.

**Steps:**
1. Go to https://github.com/new
2. Repository name: `orion`
3. Description: `Open source passive signal intelligence platform. WiFi + BLE scanning, OSINT enrichment, tactical HUD. Termux (Android) + Raspberry Pi + Linux.`
4. Set to **Public**
5. Check **Add a README file**
6. Choose **MIT License**
7. `.gitignore` template: **Python**
8. Click **Create repository**

**After repo is created, generate a Personal Access Token (PAT):**
1. GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Click **Generate new token (classic)**
3. Note: `orion-deploy`
4. Expiration: 90 days (or No expiration for dev)
5. Scopes: check `repo` (full control of private repositories)
6. Click **Generate token**
7. **COPY THE TOKEN IMMEDIATELY** — it will not be shown again
8. Store in: `C:\Projects\orion\.env` as `GITHUB_TOKEN=ghp_xxxxxxxxxxxx`

**Your GitHub Remote URL will be:**
```
https://github.com/YOUR_GITHUB_USERNAME/orion.git
```

### 0.2 — Claude Action: Initialize Local Repository

Claude executes these commands after the human provides their GitHub username and PAT.

```bash
# Windows PowerShell / cmd
mkdir C:\Projects\orion
cd C:\Projects\orion
git init
git remote add origin https://YOUR_GITHUB_USERNAME:YOUR_PAT@github.com/YOUR_GITHUB_USERNAME/orion.git
git pull origin main
```

If pulling fails (empty repo), initialize instead:
```bash
cd C:\Projects\orion
git init
git remote add origin https://YOUR_GITHUB_USERNAME:YOUR_PAT@github.com/YOUR_GITHUB_USERNAME/orion.git
```

### 0.3 — .env File (Never Commit This)

Create `C:\Projects\orion\.env`:
```env
# GitHub
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your_username_here

# Optional enrichment API keys (leave blank to disable)
WIGLE_API_NAME=
WIGLE_API_TOKEN=
SHODAN_API_KEY=
MACADDRESS_IO_KEY=
GOOGLE_GEO_API_KEY=

# App settings
ORION_PORT=5000
ORION_HOST=127.0.0.1
ORION_DEBUG=false
ORION_LOG_LEVEL=INFO
```

Ensure `.env` is in `.gitignore`:
```
.env
*.env
__pycache__/
*.pyc
*.pyo
orion.db
logs/
node_modules/
.DS_Store
```

---

## PHASE 1: DIRECTORY STRUCTURE

Claude must create this exact directory tree. Do not deviate.

```
C:\Projects\orion\
├── .env                          # Never committed
├── .gitignore
├── README.md
├── LICENSE
├── requirements.txt
├── requirements-dev.txt
├── install.sh                    # Linux/Android one-command installer
├── install_windows.bat           # Windows dev environment setup
├── run.bat                       # Windows launcher
├── run.sh                        # Linux/Android launcher
├── orion.py                      # Main entry point
│
├── core/                         # Core application
│   ├── __init__.py
│   ├── app.py                    # Flask app factory
│   ├── config.py                 # Configuration loader
│   ├── database.py               # SQLite ORM layer
│   └── logger.py                 # Structured logging
│
├── scanners/                     # Signal scanning modules
│   ├── __init__.py
│   ├── wifi_scanner.py           # WiFi via termux-wifi-scaninfo / iwlist
│   ├── ble_scanner.py            # BLE via bluetoothctl / bleak
│   ├── network_scanner.py        # LAN via arp + nmap
│   └── scanner_manager.py        # Orchestrates all scanners
│
├── analysis/                     # Signal analysis and classification
│   ├── __init__.py
│   ├── device_classifier.py      # Transient vs Static vs Mobile
│   ├── risk_scorer.py            # Signal risk scoring engine
│   ├── pattern_detector.py       # Behavioral pattern analysis
│   ├── ssid_analyzer.py          # SSID identity extraction
│   └── baseline_manager.py       # Environmental baseline profiling
│
├── enrichment/                   # OSINT enrichment modules (optional/online)
│   ├── __init__.py
│   ├── oui_lookup.py             # Local IEEE OUI database
│   ├── wigle_lookup.py           # WiGLE BSSID geolocation
│   ├── shodan_lookup.py          # Shodan IP/device lookup
│   ├── macaddress_lookup.py      # macaddress.io vendor details
│   ├── nvd_lookup.py             # NIST CVE database
│   ├── bt_uuid_lookup.py         # Bluetooth SIG UUID registry
│   └── enrichment_manager.py     # Orchestrates all enrichment
│
├── intel/                        # Intelligence operations
│   ├── __init__.py
│   ├── timeline.py               # Intel Timeline log manager
│   ├── debrief_generator.py      # Export debrief engine
│   ├── alert_manager.py          # Alert rules and notifications
│   └── report_builder.py        # Report generation
│
├── api/                          # Flask REST API routes
│   ├── __init__.py
│   ├── scan_routes.py            # /api/scan/*
│   ├── device_routes.py          # /api/devices/*
│   ├── intel_routes.py           # /api/intel/*
│   ├── enrichment_routes.py      # /api/enrich/*
│   ├── settings_routes.py        # /api/settings/*
│   └── alert_routes.py           # /api/alerts/*
│
├── static/                       # Frontend static assets
│   ├── css/
│   │   ├── base.css              # Variables, resets, typography
│   │   ├── hud.css               # HUD/radar screen styles
│   │   ├── timeline.css          # Intel Timeline styles
│   │   ├── devices.css           # Device list/grid styles
│   │   ├── enrichment.css        # Enrichment panel styles
│   │   ├── settings.css          # Settings screen styles
│   │   └── alerts.css            # Alert overlay styles
│   ├── js/
│   │   ├── api.js                # API client (fetch wrapper)
│   │   ├── radar.js              # Canvas radar renderer
│   │   ├── timeline.js           # Timeline feed controller
│   │   ├── devices.js            # Device table controller
│   │   ├── enrichment.js         # Enrichment panel controller
│   │   ├── alerts.js             # Alert overlay controller
│   │   ├── settings.js           # Settings form controller
│   │   └── app.js                # Main app bootstrap
│   └── data/
│       ├── oui.json              # IEEE OUI database (bundled)
│       ├── bt_uuids.json         # Bluetooth SIG UUID registry
│       ├── camera_ouis.txt       # Known camera vendor OUI list
│       ├── evil_ssids.txt        # Known malicious/suspicious SSID patterns
│       └── router_patterns.txt   # Router default SSID patterns
│
├── templates/                    # Jinja2 HTML templates
│   ├── base.html                 # Base layout
│   ├── hud.html                  # Main HUD / radar screen
│   ├── timeline.html             # Intel Timeline screen
│   ├── devices.html              # Device inventory screen
│   ├── enrichment.html           # OSINT enrichment screen
│   ├── settings.html             # Settings screen
│   ├── alerts.html               # Alerts/notifications screen
│   └── debrief.html              # Debrief export screen
│
├── data/                         # Runtime data (gitignored)
│   ├── orion.db                  # SQLite database
│   └── logs/                     # Log files
│
└── tests/                        # Test suite
    ├── __init__.py
    ├── test_wifi_scanner.py
    ├── test_ble_scanner.py
    ├── test_network_scanner.py
    ├── test_risk_scorer.py
    ├── test_oui_lookup.py
    ├── test_device_classifier.py
    ├── test_api_scan.py
    └── test_api_intel.py
```

---

## PHASE 2: DEPENDENCIES

### requirements.txt
```
flask==3.0.3
flask-cors==4.0.1
python-dotenv==1.0.1
requests==2.32.3
schedule==1.2.2
bleak==0.22.3
scapy==2.5.0
netifaces==0.11.0
psutil==6.0.0
python-nmap==0.7.1
```

### requirements-dev.txt
```
pytest==8.2.2
pytest-asyncio==0.23.7
black==24.4.2
flake8==7.1.0
coverage==7.5.3
```

### Platform notes:
- `bleak` handles BLE on Linux/Pi. On Android/Termux it is **not supported** — Termux uses `termux-bluetooth-scaninfo` via subprocess instead.
- `python-nmap` requires nmap binary: `pkg install nmap` (Termux) or `apt install nmap` (Pi/Linux)
- `scapy` requires root on some platforms for raw sockets. For passive-only use, it is optional.

---

## PHASE 3: CORE APPLICATION

### 3.1 — orion.py (Entry Point)

```python
#!/usr/bin/env python3
"""
ORION — Open Source Passive Signal Intelligence Platform
Entry point. Run with: python orion.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app import create_app
from core.config import Config
from core.logger import setup_logger

def main():
    config = Config()
    logger = setup_logger(config.log_level)
    logger.info("ORION v1.0.0 starting...")
    logger.info(f"Platform: {config.platform}")
    logger.info(f"Listening on {config.host}:{config.port}")

    app = create_app(config)
    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug,
        use_reloader=False,
        threaded=True
    )

if __name__ == '__main__':
    main()
```

### 3.2 — core/config.py

```python
import os
import platform
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        # App
        self.host = os.getenv('ORION_HOST', '127.0.0.1')
        self.port = int(os.getenv('ORION_PORT', 5000))
        self.debug = os.getenv('ORION_DEBUG', 'false').lower() == 'true'
        self.log_level = os.getenv('ORION_LOG_LEVEL', 'INFO')

        # Platform detection
        system = platform.system().lower()
        machine = platform.machine().lower()
        if 'android' in os.environ.get('PREFIX', '').lower() or os.path.exists('/data/data/com.termux'):
            self.platform = 'termux'
        elif system == 'linux' and ('arm' in machine or 'aarch' in machine):
            self.platform = 'raspberrypi'
        elif system == 'linux':
            self.platform = 'linux'
        elif system == 'windows':
            self.platform = 'windows'
        else:
            self.platform = 'unknown'

        # Paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.static_dir = os.path.join(self.base_dir, 'static')
        self.db_path = os.path.join(self.data_dir, 'orion.db')
        self.oui_path = os.path.join(self.static_dir, 'data', 'oui.json')
        self.bt_uuid_path = os.path.join(self.static_dir, 'data', 'bt_uuids.json')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'logs'), exist_ok=True)

        # Scan intervals (seconds)
        self.wifi_scan_interval = int(os.getenv('WIFI_SCAN_INTERVAL', 30))
        self.ble_scan_interval = int(os.getenv('BLE_SCAN_INTERVAL', 20))
        self.network_scan_interval = int(os.getenv('NETWORK_SCAN_INTERVAL', 120))

        # Risk scoring
        self.risk_score_threshold_warn = int(os.getenv('RISK_WARN_THRESHOLD', 50))
        self.risk_score_threshold_alert = int(os.getenv('RISK_ALERT_THRESHOLD', 75))

        # Enrichment API keys (all optional)
        self.wigle_api_name = os.getenv('WIGLE_API_NAME', '')
        self.wigle_api_token = os.getenv('WIGLE_API_TOKEN', '')
        self.shodan_api_key = os.getenv('SHODAN_API_KEY', '')
        self.macaddress_io_key = os.getenv('MACADDRESS_IO_KEY', '')
        self.google_geo_api_key = os.getenv('GOOGLE_GEO_API_KEY', '')

        # Feature flags
        self.enable_wifi_scan = os.getenv('ENABLE_WIFI', 'true').lower() == 'true'
        self.enable_ble_scan = os.getenv('ENABLE_BLE', 'true').lower() == 'true'
        self.enable_network_scan = os.getenv('ENABLE_NETWORK', 'true').lower() == 'true'
        self.enable_enrichment = os.getenv('ENABLE_ENRICHMENT', 'false').lower() == 'true'
        self.enable_wigle_contrib = os.getenv('ENABLE_WIGLE_CONTRIB', 'false').lower() == 'true'
```

### 3.3 — core/database.py

```python
import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
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
        now = datetime.utcnow().isoformat()
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
        now = datetime.utcnow().isoformat()
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
        now = datetime.utcnow().isoformat()
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

    def get_scan_history(self, minutes: int = 5) -> list:
        cutoff = datetime.utcnow().isoformat()
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT * FROM scan_events
                WHERE scan_time >= datetime('now', ?)
                ORDER BY scan_time ASC
            """, (f'-{minutes} minutes',)).fetchall()
            return [dict(r) for r in rows]
```

### 3.4 — core/app.py

```python
from flask import Flask
from flask_cors import CORS

def create_app(config):
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )
    app.config['SECRET_KEY'] = 'orion-dev-key-change-in-prod'
    app.config['ORION_CONFIG'] = config
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize database
    from core.database import Database
    db = Database(config.db_path)
    app.config['DB'] = db

    # Initialize scanner manager
    from scanners.scanner_manager import ScannerManager
    scanner_manager = ScannerManager(config, db)
    app.config['SCANNER'] = scanner_manager
    scanner_manager.start()

    # Register blueprints
    from api.scan_routes import scan_bp
    from api.device_routes import device_bp
    from api.intel_routes import intel_bp
    from api.enrichment_routes import enrichment_bp
    from api.settings_routes import settings_bp
    from api.alert_routes import alert_bp

    app.register_blueprint(scan_bp, url_prefix='/api/scan')
    app.register_blueprint(device_bp, url_prefix='/api/devices')
    app.register_blueprint(intel_bp, url_prefix='/api/intel')
    app.register_blueprint(enrichment_bp, url_prefix='/api/enrich')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(alert_bp, url_prefix='/api/alerts')

    # Register UI routes
    from api.ui_routes import ui_bp
    app.register_blueprint(ui_bp)

    return app
```

---

## PHASE 4: SCANNER MODULES

### 4.1 — scanners/wifi_scanner.py

```python
import subprocess
import json
import os
import math
from typing import List, Dict

class WiFiScanner:
    """
    Platform-aware WiFi scanner.
    Termux: uses termux-wifi-scaninfo
    Linux/Pi: uses iwlist or nmcli
    Windows: uses netsh wlan show networks
    """

    def __init__(self, config):
        self.config = config
        self.platform = config.platform

    def scan(self) -> List[Dict]:
        if self.platform == 'termux':
            return self._scan_termux()
        elif self.platform in ('linux', 'raspberrypi'):
            return self._scan_linux()
        elif self.platform == 'windows':
            return self._scan_windows()
        else:
            return self._scan_mock()

    def _scan_termux(self) -> List[Dict]:
        try:
            result = subprocess.run(
                ['termux-wifi-scaninfo'],
                capture_output=True, text=True, timeout=10
            )
            raw = json.loads(result.stdout)
            return [self._normalize_termux(ap) for ap in raw]
        except Exception as e:
            return []

    def _normalize_termux(self, ap: dict) -> dict:
        rssi = ap.get('rssi', -100)
        freq = ap.get('frequency_mhz', 2412)
        return {
            'mac': ap.get('bssid', '').upper(),
            'ssid': ap.get('ssid', '') or '',
            'rssi': rssi,
            'frequency_mhz': freq,
            'channel': self._freq_to_channel(freq),
            'band': '5GHz' if freq > 4900 else '2.4GHz',
            'security': ap.get('capabilities', 'OPEN'),
            'hidden': len(ap.get('ssid', '').strip()) == 0,
            'distance_m': self._estimate_distance(rssi),
            'source': 'termux'
        }

    def _scan_linux(self) -> List[Dict]:
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'BSSID,SSID,FREQ,SIGNAL,SECURITY',
                 'device', 'wifi', 'list'],
                capture_output=True, text=True, timeout=15
            )
            devices = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split(':')
                if len(parts) >= 5:
                    mac = ':'.join(parts[:6]).upper() if len(parts) >= 6 else parts[0]
                    # nmcli uses escaped colons - handle properly
                    devices.append(self._parse_nmcli_line(line))
            return [d for d in devices if d]
        except FileNotFoundError:
            return self._scan_iwlist()

    def _scan_iwlist(self) -> List[Dict]:
        """Fallback for systems without nmcli."""
        interfaces = self._get_wifi_interfaces()
        if not interfaces:
            return []
        try:
            result = subprocess.run(
                ['iwlist', interfaces[0], 'scan'],
                capture_output=True, text=True, timeout=20
            )
            return self._parse_iwlist_output(result.stdout)
        except Exception:
            return []

    def _scan_windows(self) -> List[Dict]:
        """Windows netsh fallback for dev testing."""
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                capture_output=True, text=True, timeout=10,
                encoding='utf-8', errors='replace'
            )
            return self._parse_netsh_output(result.stdout)
        except Exception:
            return []

    def _scan_mock(self) -> List[Dict]:
        """Returns mock data for testing when no scanner is available."""
        import random
        return [
            {
                'mac': f'AA:BB:CC:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}',
                'ssid': f'TestNetwork_{i}',
                'rssi': random.randint(-90, -30),
                'frequency_mhz': random.choice([2412, 2437, 5180, 5220]),
                'channel': random.choice([1, 6, 11, 36, 40]),
                'band': '2.4GHz',
                'security': random.choice(['WPA2', 'WPA3', 'OPEN']),
                'hidden': False,
                'distance_m': random.uniform(1, 50),
                'source': 'mock'
            }
            for i in range(random.randint(3, 12))
        ]

    def _get_wifi_interfaces(self) -> List[str]:
        try:
            result = subprocess.run(
                ['iwconfig'], capture_output=True, text=True
            )
            interfaces = []
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line:
                    interfaces.append(line.split()[0])
            return interfaces
        except Exception:
            return ['wlan0']

    def _freq_to_channel(self, freq_mhz: int) -> int:
        if freq_mhz == 2412: return 1
        if freq_mhz == 2417: return 2
        if freq_mhz == 2422: return 3
        if freq_mhz == 2427: return 4
        if freq_mhz == 2432: return 5
        if freq_mhz == 2437: return 6
        if freq_mhz == 2442: return 7
        if freq_mhz == 2447: return 8
        if freq_mhz == 2452: return 9
        if freq_mhz == 2457: return 10
        if freq_mhz == 2462: return 11
        if 5000 <= freq_mhz <= 5900:
            return (freq_mhz - 5000) // 5
        return 0

    def _estimate_distance(self, rssi: int, tx_power: int = -59, n: float = 2.5) -> float:
        """
        RSSI-based distance estimate. Highly approximate.
        Formula: distance = 10 ^ ((TxPower - RSSI) / (10 * n))
        tx_power: signal strength at 1 meter (-59 dBm typical)
        n: path loss exponent (2=free space, 2.5=typical indoor, 3=heavy indoor)
        """
        if rssi == 0:
            return -1.0
        try:
            return round(10 ** ((tx_power - rssi) / (10 * n)), 1)
        except Exception:
            return -1.0

    def _parse_nmcli_line(self, line: str) -> dict:
        # nmcli -t escapes colons in values with backslash
        # Format: BSSID:SSID:FREQ:SIGNAL:SECURITY
        # BSSIDs contain colons so we need special parsing
        try:
            # Replace escaped colons temporarily
            safe = line.replace('\\:', '\x00')
            parts = safe.split(':')
            # Reconstruct BSSID (first 6 hex pairs + colons)
            bssid_parts = parts[:6]
            bssid = ':'.join(p.replace('\x00', ':') for p in bssid_parts).upper()
            remaining = parts[6:]
            if len(remaining) >= 4:
                ssid = remaining[0].replace('\x00', ':')
                freq_str = remaining[1].replace('\x00', ':')
                signal = int(remaining[2]) if remaining[2].strip().isdigit() else -70
                security = remaining[3].replace('\x00', ':').strip()
                freq_mhz = int(''.join(filter(str.isdigit, freq_str[:5]))) if freq_str else 2412
                rssi = (signal * 2) - 100  # nmcli reports 0-100, convert to dBm approx
                return {
                    'mac': bssid,
                    'ssid': ssid,
                    'rssi': rssi,
                    'frequency_mhz': freq_mhz,
                    'channel': self._freq_to_channel(freq_mhz),
                    'band': '5GHz' if freq_mhz > 4900 else '2.4GHz',
                    'security': security if security else 'OPEN',
                    'hidden': not bool(ssid.strip()),
                    'distance_m': self._estimate_distance(rssi),
                    'source': 'nmcli'
                }
        except Exception:
            return None

    def _parse_iwlist_output(self, output: str) -> list:
        devices = []
        current = {}
        for line in output.split('\n'):
            line = line.strip()
            if 'Cell' in line and 'Address:' in line:
                if current.get('mac'):
                    devices.append(current)
                current = {'mac': line.split('Address:')[1].strip().upper()}
            elif 'ESSID:' in line:
                current['ssid'] = line.split('ESSID:')[1].strip().strip('"')
            elif 'Frequency:' in line:
                try:
                    freq_ghz = float(line.split('Frequency:')[1].split(' ')[0])
                    current['frequency_mhz'] = int(freq_ghz * 1000)
                except Exception:
                    current['frequency_mhz'] = 2412
            elif 'Signal level=' in line:
                try:
                    rssi = int(line.split('Signal level=')[1].split(' ')[0].split('/')[0])
                    if rssi > 0: rssi = rssi - 100
                    current['rssi'] = rssi
                    current['distance_m'] = self._estimate_distance(rssi)
                except Exception:
                    current['rssi'] = -80
            elif 'Encryption key:' in line:
                current['security'] = 'WPA2' if 'on' in line else 'OPEN'
        if current.get('mac'):
            devices.append(current)
        return devices

    def _parse_netsh_output(self, output: str) -> list:
        devices = []
        current = {}
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('SSID') and ':' in line and 'BSSID' not in line:
                if current.get('ssid'):
                    devices.append(current)
                current = {'ssid': line.split(':', 1)[1].strip()}
            elif 'BSSID 1' in line:
                current['mac'] = line.split(':', 1)[1].strip().upper()
            elif 'Signal' in line:
                try:
                    pct = int(line.split(':')[1].strip().replace('%', ''))
                    current['rssi'] = (pct // 2) - 100
                    current['distance_m'] = self._estimate_distance(current['rssi'])
                except Exception:
                    current['rssi'] = -70
            elif 'Authentication' in line:
                current['security'] = line.split(':', 1)[1].strip()
        if current.get('ssid'):
            devices.append(current)
        # Fill in defaults
        for d in devices:
            d.setdefault('frequency_mhz', 2412)
            d.setdefault('channel', 6)
            d.setdefault('band', '2.4GHz')
            d.setdefault('hidden', False)
            d.setdefault('source', 'netsh')
        return devices
```

### 4.2 — scanners/ble_scanner.py

```python
import subprocess
import json
import asyncio
import threading
from typing import List, Dict

class BLEScanner:
    """
    Platform-aware BLE scanner.
    Termux: termux-bluetooth-scaninfo (unofficial) or bluetoothctl via proot
    Linux/Pi: bleak or bluetoothctl subprocess
    Windows: bleak
    """

    APPLE_MFID = 0x004C
    MICROSOFT_MFID = 0x0006
    GOOGLE_MFID = 0x00E0

    # Known BLE device type fingerprints
    AIRTAG_PAYLOAD_MARKER = bytes([0x12, 0x19])  # Simplified — real detection is more complex

    def __init__(self, config):
        self.config = config
        self.platform = config.platform
        self._scan_results = []
        self._scanning = False

    def scan(self) -> List[Dict]:
        if self.platform == 'termux':
            return self._scan_termux()
        elif self.platform in ('linux', 'raspberrypi'):
            return self._scan_linux()
        elif self.platform == 'windows':
            return self._scan_windows_bleak()
        else:
            return self._scan_mock()

    def _scan_termux(self) -> List[Dict]:
        """
        On Termux, native BLE scanning via bluetoothctl.
        Requires: pkg install bluez (where available) or use termux-bluetooth-scaninfo
        from unofficial fork: github.com/StevenSalazarM/Termux-api-bluetooth
        Falls back to empty list if unavailable.
        """
        try:
            # Try termux-bluetooth-scaninfo (unofficial)
            result = subprocess.run(
                ['termux-bluetooth-scaninfo'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                raw = json.loads(result.stdout)
                return [self._normalize_ble_device(d) for d in raw]
        except Exception:
            pass

        # Fallback: bluetoothctl scan for 5 seconds
        try:
            proc = subprocess.Popen(
                ['bluetoothctl'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            commands = "scan on\n"
            import time
            time.sleep(5)
            commands += "devices\nscan off\nexit\n"
            stdout, _ = proc.communicate(input=commands, timeout=10)
            return self._parse_bluetoothctl_output(stdout)
        except Exception:
            return []

    def _scan_linux(self) -> List[Dict]:
        """Use bleak for async BLE scanning on Linux/Pi."""
        try:
            import bleak
            loop = asyncio.new_event_loop()
            devices = loop.run_until_complete(self._bleak_scan())
            loop.close()
            return devices
        except ImportError:
            return self._bluetoothctl_scan()

    async def _bleak_scan(self, timeout: float = 5.0) -> List[Dict]:
        from bleak import BleakScanner
        devices = await BleakScanner.discover(timeout=timeout, return_adv=True)
        result = []
        for addr, (device, adv) in devices.items():
            mfr_data = adv.manufacturer_data if adv.manufacturer_data else {}
            rssi = adv.rssi if adv.rssi else -100
            result.append({
                'mac': addr.upper(),
                'name': device.name or '',
                'rssi': rssi,
                'distance_m': self._estimate_ble_distance(rssi),
                'manufacturer_data': {k: v.hex() for k, v in mfr_data.items()},
                'service_uuids': adv.service_uuids or [],
                'device_hints': self._fingerprint_ble_device(mfr_data, adv.service_uuids or []),
                'is_apple': self.APPLE_MFID in mfr_data,
                'is_airtag': self._is_airtag(mfr_data),
                'source': 'bleak'
            })
        return result

    def _scan_windows_bleak(self) -> List[Dict]:
        """Windows uses bleak with WinRT backend."""
        try:
            import bleak
            loop = asyncio.new_event_loop()
            devices = loop.run_until_complete(self._bleak_scan(timeout=4.0))
            loop.close()
            return devices
        except Exception:
            return self._scan_mock_ble()

    def _bluetoothctl_scan(self) -> List[Dict]:
        try:
            import time
            proc = subprocess.Popen(
                ['bluetoothctl'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True
            )
            time.sleep(5)
            stdout, _ = proc.communicate(input="scan on\ndevices\nscan off\nexit\n", timeout=10)
            return self._parse_bluetoothctl_output(stdout)
        except Exception:
            return []

    def _parse_bluetoothctl_output(self, output: str) -> List[Dict]:
        devices = []
        for line in output.split('\n'):
            if 'Device' in line and ':' in line:
                parts = line.strip().split(' ')
                try:
                    mac_idx = next(i for i, p in enumerate(parts) if len(p) == 17 and p.count(':') == 5)
                    mac = parts[mac_idx].upper()
                    name = ' '.join(parts[mac_idx+1:]) if len(parts) > mac_idx+1 else ''
                    devices.append({
                        'mac': mac,
                        'name': name,
                        'rssi': -70,  # bluetoothctl doesn't always give RSSI
                        'distance_m': -1,
                        'manufacturer_data': {},
                        'service_uuids': [],
                        'device_hints': [],
                        'is_apple': False,
                        'is_airtag': False,
                        'source': 'bluetoothctl'
                    })
                except Exception:
                    continue
        return devices

    def _normalize_ble_device(self, raw: dict) -> dict:
        rssi = raw.get('rssi', -100)
        return {
            'mac': raw.get('address', raw.get('mac', '')).upper(),
            'name': raw.get('name', ''),
            'rssi': rssi,
            'distance_m': self._estimate_ble_distance(rssi),
            'manufacturer_data': raw.get('manufacturer_data', {}),
            'service_uuids': raw.get('service_uuids', []),
            'device_hints': [],
            'is_apple': False,
            'is_airtag': False,
            'source': 'termux'
        }

    def _is_airtag(self, manufacturer_data: dict) -> bool:
        """
        Detect AirTag by Apple manufacturer ID (0x004C) + specific payload length/type.
        Simplified detection — full detection requires parsing Apple's FindMy payload.
        Payload bytes for AirTag: company ID 0x4C00, type 0x12, length 0x19
        """
        if self.APPLE_MFID not in manufacturer_data:
            return False
        payload = manufacturer_data[self.APPLE_MFID]
        if isinstance(payload, bytes) and len(payload) >= 2:
            return payload[0] == 0x12 and payload[1] == 0x19
        return False

    def _fingerprint_ble_device(self, mfr_data: dict, service_uuids: list) -> list:
        hints = []
        if self.APPLE_MFID in mfr_data:
            payload = mfr_data[self.APPLE_MFID]
            if isinstance(payload, bytes):
                if len(payload) >= 2 and payload[0] == 0x12:
                    hints.append('AIRTAG_CANDIDATE')
                elif len(payload) >= 2 and payload[0] == 0x09:
                    hints.append('AIRPODS')
                elif len(payload) >= 2 and payload[0] == 0x10:
                    hints.append('IPHONE_NEARBY')
        if self.MICROSOFT_MFID in mfr_data:
            hints.append('WINDOWS_DEVICE')
        if self.GOOGLE_MFID in mfr_data:
            hints.append('ANDROID_NEARBY')
        # Check service UUIDs for common types
        uuid_map = {
            '0000180f': 'BATTERY_SERVICE',
            '0000180d': 'HEART_RATE',
            '0000181c': 'USER_DATA',
            '0000feaa': 'EDDYSTONE_BEACON',
            '0000fd6f': 'COVID_EXPOSURE',
            '0000fe9f': 'GOOGLE_NEARBY',
            '0000fe2c': 'GOOGLE_FAST_PAIR',
        }
        for uuid in service_uuids:
            short = uuid.lower().replace('-', '')[:8]
            if short in uuid_map:
                hints.append(uuid_map[short])
        return hints

    def _estimate_ble_distance(self, rssi: int, tx_power: int = -65) -> float:
        if rssi == 0:
            return -1.0
        try:
            return round(10 ** ((tx_power - rssi) / 20), 1)
        except Exception:
            return -1.0

    def _scan_mock_ble(self) -> List[Dict]:
        import random
        vendors = ['Apple', 'Samsung', 'Fitbit', 'Unknown', 'Espressif']
        return [
            {
                'mac': f'CC:DD:EE:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}',
                'name': random.choice(['', 'FitBit', 'iPhone', 'Galaxy Watch', '']),
                'rssi': random.randint(-90, -35),
                'distance_m': random.uniform(0.5, 20),
                'manufacturer_data': {},
                'service_uuids': [],
                'device_hints': [],
                'is_apple': random.random() > 0.7,
                'is_airtag': False,
                'source': 'mock'
            }
            for i in range(random.randint(2, 8))
        ]
```

### 4.3 — scanners/network_scanner.py

```python
import subprocess
import re
import json
from typing import List, Dict

class NetworkScanner:
    """
    LAN device scanner.
    Uses arp -a (passive, always available) + optional nmap ping sweep.
    No root required for basic operation.
    """

    SUSPICIOUS_PORTS = [554, 8554, 8080, 80, 443, 23, 21]  # RTSP, HTTP, Telnet, FTP
    CAMERA_PORTS = [554, 8554]

    def __init__(self, config):
        self.config = config

    def scan_arp(self) -> List[Dict]:
        """Fast passive scan using ARP cache."""
        try:
            result = subprocess.run(
                ['arp', '-a'],
                capture_output=True, text=True, timeout=10
            )
            return self._parse_arp_output(result.stdout)
        except Exception:
            return []

    def scan_subnet(self, subnet: str = None) -> List[Dict]:
        """Ping sweep using nmap. Requires nmap installed."""
        if not subnet:
            subnet = self._get_local_subnet()
        if not subnet:
            return self.scan_arp()
        try:
            result = subprocess.run(
                ['nmap', '-sn', '--open', subnet],
                capture_output=True, text=True, timeout=60
            )
            return self._parse_nmap_output(result.stdout)
        except FileNotFoundError:
            return self.scan_arp()

    def probe_device(self, ip: str) -> Dict:
        """Check common ports on a device to identify type."""
        try:
            result = subprocess.run(
                ['nmap', '-p', ','.join(str(p) for p in self.SUSPICIOUS_PORTS),
                 '--open', ip],
                capture_output=True, text=True, timeout=30
            )
            open_ports = self._extract_open_ports(result.stdout)
            device_type = 'unknown'
            if any(p in open_ports for p in self.CAMERA_PORTS):
                device_type = 'ip_camera'
            elif 23 in open_ports:
                device_type = 'telnet_device'
            return {'ip': ip, 'open_ports': open_ports, 'device_type': device_type}
        except Exception:
            return {'ip': ip, 'open_ports': [], 'device_type': 'unknown'}

    def _parse_arp_output(self, output: str) -> List[Dict]:
        devices = []
        for line in output.split('\n'):
            # Match: hostname (IP) at MAC [ether] on interface
            match = re.search(
                r'[\w.-]*\s*\(?([\d.]+)\)?\s+at\s+([0-9a-fA-F:]{17})',
                line
            )
            if match:
                ip = match.group(1)
                mac = match.group(2).upper()
                if mac not in ('<incomplete>', 'FF:FF:FF:FF:FF:FF'):
                    devices.append({
                        'ip': ip,
                        'mac': mac,
                        'hostname': self._extract_hostname(line),
                        'source': 'arp'
                    })
        return devices

    def _parse_nmap_output(self, output: str) -> List[Dict]:
        devices = []
        current = {}
        for line in output.split('\n'):
            if 'Nmap scan report for' in line:
                if current.get('ip'):
                    devices.append(current)
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                hostname = line.replace('Nmap scan report for', '').strip()
                current = {
                    'ip': ip_match.group(1) if ip_match else '',
                    'hostname': hostname,
                    'mac': '',
                    'source': 'nmap'
                }
            elif 'MAC Address:' in line:
                mac_match = re.search(r'([0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2})', line.upper())
                if mac_match:
                    current['mac'] = mac_match.group(1)
        if current.get('ip'):
            devices.append(current)
        return devices

    def _extract_open_ports(self, nmap_output: str) -> List[int]:
        ports = []
        for line in nmap_output.split('\n'):
            match = re.match(r'\s*(\d+)/tcp\s+open', line)
            if match:
                ports.append(int(match.group(1)))
        return ports

    def _extract_hostname(self, line: str) -> str:
        parts = line.split()
        if parts and '(' not in parts[0]:
            return parts[0]
        return ''

    def _get_local_subnet(self) -> str:
        """Determine local subnet for scanning."""
        try:
            import netifaces
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr.get('addr', '')
                        if ip and not ip.startswith('127.'):
                            parts = ip.split('.')
                            return f"{'.'.join(parts[:3])}.0/24"
        except Exception:
            pass
        return '192.168.1.0/24'
```

### 4.4 — scanners/scanner_manager.py

```python
import threading
import time
import schedule
from typing import Callable

class ScannerManager:
    def __init__(self, config, db):
        self.config = config
        self.db = db
        self._thread = None
        self._running = False
        self._last_wifi_results = []
        self._last_ble_results = []
        self._last_network_results = []

        # Import scanners
        from scanners.wifi_scanner import WiFiScanner
        from scanners.ble_scanner import BLEScanner
        from scanners.network_scanner import NetworkScanner
        from analysis.device_classifier import DeviceClassifier
        from analysis.risk_scorer import RiskScorer
        from enrichment.oui_lookup import OUILookup
        from intel.alert_manager import AlertManager

        self.wifi_scanner = WiFiScanner(config)
        self.ble_scanner = BLEScanner(config)
        self.network_scanner = NetworkScanner(config)
        self.classifier = DeviceClassifier(db)
        self.risk_scorer = RiskScorer(config)
        self.oui_lookup = OUILookup(config.oui_path)
        self.alert_manager = AlertManager(db)

    def start(self):
        self._running = True
        if self.config.enable_wifi_scan:
            schedule.every(self.config.wifi_scan_interval).seconds.do(self._run_wifi_scan)
        if self.config.enable_ble_scan:
            schedule.every(self.config.ble_scan_interval).seconds.do(self._run_ble_scan)
        if self.config.enable_network_scan:
            schedule.every(self.config.network_scan_interval).seconds.do(self._run_network_scan)

        # Run initial scans immediately
        threading.Thread(target=self._run_wifi_scan, daemon=True).start()
        threading.Thread(target=self._run_ble_scan, daemon=True).start()

        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        schedule.clear()

    def _scheduler_loop(self):
        while self._running:
            schedule.run_pending()
            time.sleep(1)

    def _run_wifi_scan(self):
        try:
            devices = self.wifi_scanner.scan()
            for device in devices:
                mac = device.get('mac')
                if not mac:
                    continue
                vendor = self.oui_lookup.lookup(mac)
                device['vendor'] = vendor
                risk = self.risk_scorer.score_wifi(device)
                device['risk_score'] = risk['score']
                device['risk_flags'] = risk['flags']
                classification = self.classifier.classify(mac, 'wifi', device)
                device['classification'] = classification
                self.db.upsert_device(mac, 'wifi', device)
                self.db.log_scan_event('wifi', mac, device)
                self.alert_manager.evaluate_wifi(device)
            self._last_wifi_results = devices
        except Exception as e:
            pass

    def _run_ble_scan(self):
        try:
            devices = self.ble_scanner.scan()
            for device in devices:
                mac = device.get('mac')
                if not mac:
                    continue
                vendor = self.oui_lookup.lookup(mac)
                device['vendor'] = vendor
                risk = self.risk_scorer.score_ble(device)
                device['risk_score'] = risk['score']
                device['risk_flags'] = risk['flags']
                classification = self.classifier.classify(mac, 'ble', device)
                device['classification'] = classification
                self.db.upsert_device(mac, 'ble', device)
                self.db.log_scan_event('ble', mac, device)
                self.alert_manager.evaluate_ble(device)
            self._last_ble_results = devices
        except Exception as e:
            pass

    def _run_network_scan(self):
        try:
            devices = self.network_scanner.scan_arp()
            for device in devices:
                mac = device.get('mac')
                if not mac:
                    continue
                vendor = self.oui_lookup.lookup(mac)
                device['vendor'] = vendor
                device['device_type'] = 'network'
                risk = self.risk_scorer.score_network(device)
                device['risk_score'] = risk['score']
                device['risk_flags'] = risk['flags']
                self.db.upsert_device(mac, 'network', device)
                self.db.log_scan_event('network', mac, device)
            self._last_network_results = devices
        except Exception as e:
            pass

    def get_current_state(self) -> dict:
        return {
            'wifi': self._last_wifi_results,
            'ble': self._last_ble_results,
            'network': self._last_network_results,
            'wifi_count': len(self._last_wifi_results),
            'ble_count': len(self._last_ble_results),
            'network_count': len(self._last_network_results)
        }
```

---

## PHASE 5: ANALYSIS MODULES

### 5.1 — analysis/risk_scorer.py

```python
class RiskScorer:
    """
    Scores WiFi, BLE, and network devices on a 0-100 risk scale.
    Returns score + list of flag strings.
    """

    KNOWN_CAMERA_OUIS = {
        '24:0A:C4', '30:AE:A4', '24:6F:28', '3C:61:05',  # Espressif (DIY cameras)
        'D4:5D:64', 'B4:A2:EB', 'BC:32:5F',              # Hikvision
        'E0:0A:F6', '8C:E7:48', 'AC:CF:85',              # Dahua
        'DC:44:27', 'C8:02:8F',                           # Reolink
        'E4:AB:89',                                        # Amcrest
    }

    SUSPICIOUS_SSID_PATTERNS = [
        'cam', 'camera', 'spy', 'hidden', 'reolink', 'hikvision',
        'dahua', 'wyze', 'ring', 'nest', 'arlo', 'blink',
        'ip-cam', 'ipcam', 'nvr', 'dvr', 'cctv'
    ]

    DEFAULT_ROUTER_PATTERNS = [
        'netgear', 'linksys', 'tp-link', 'tplink', 'fritz',
        'xfinity', 'spectrum', 'att-', 'default', 'dlink'
    ]

    def score_wifi(self, device: dict) -> dict:
        score = 0
        flags = []
        ssid = (device.get('ssid') or '').lower()
        security = (device.get('security') or '').upper()
        mac = (device.get('mac') or '').upper()
        rssi = device.get('rssi', -80)
        hidden = device.get('hidden', False)
        vendor = (device.get('vendor') or '').lower()

        # Open network
        if 'WPA' not in security and 'WEP' not in security:
            score += 30
            flags.append('OPEN_NETWORK')

        # Hidden SSID
        if hidden:
            score += 20
            flags.append('HIDDEN_SSID')

        # Camera-related SSID keyword
        if any(p in ssid for p in self.SUSPICIOUS_SSID_PATTERNS):
            score += 25
            flags.append('CAMERA_SSID_KEYWORD')

        # ESP/Espressif OUI (DIY device chip)
        oui = mac[:8]
        if oui in self.KNOWN_CAMERA_OUIS:
            score += 35
            flags.append('CAMERA_VENDOR_OUI')

        # Default router SSID (not a threat but informational)
        if any(p in ssid for p in self.DEFAULT_ROUTER_PATTERNS):
            score += 10
            flags.append('DEFAULT_ROUTER_SSID')

        # Very strong signal = device is close / in the room
        if rssi > -40:
            score += 10
            flags.append('VERY_STRONG_SIGNAL')

        # WEP (old/broken encryption)
        if 'WEP' in security:
            score += 15
            flags.append('WEAK_ENCRYPTION_WEP')

        return {'score': min(score, 100), 'flags': flags}

    def score_ble(self, device: dict) -> dict:
        score = 0
        flags = []
        is_airtag = device.get('is_airtag', False)
        is_apple = device.get('is_apple', False)
        hints = device.get('device_hints', [])
        name = (device.get('name') or '').lower()
        mac = (device.get('mac') or '').upper()
        rssi = device.get('rssi', -80)
        vendor = (device.get('vendor') or '').lower()

        if is_airtag:
            score += 70
            flags.append('AIRTAG_DETECTED')

        if 'AIRTAG_CANDIDATE' in hints:
            score += 50
            flags.append('AIRTAG_CANDIDATE')

        oui = mac[:8]
        if oui in self.KNOWN_CAMERA_OUIS:
            score += 40
            flags.append('CAMERA_VENDOR_OUI')

        if not name and not is_apple:
            score += 15
            flags.append('ANONYMOUS_DEVICE')

        if rssi > -45:
            score += 10
            flags.append('VERY_CLOSE_RANGE')

        return {'score': min(score, 100), 'flags': flags}

    def score_network(self, device: dict) -> dict:
        score = 0
        flags = []
        vendor = (device.get('vendor') or '').lower()
        open_ports = device.get('open_ports', [])
        mac = (device.get('mac') or '').upper()

        oui = mac[:8]
        if oui in self.KNOWN_CAMERA_OUIS:
            score += 40
            flags.append('CAMERA_VENDOR_OUI')

        if 554 in open_ports or 8554 in open_ports:
            score += 35
            flags.append('RTSP_PORT_OPEN')

        if 23 in open_ports:
            score += 20
            flags.append('TELNET_PORT_OPEN')

        if 21 in open_ports:
            score += 10
            flags.append('FTP_PORT_OPEN')

        if not vendor or vendor == 'unknown':
            score += 10
            flags.append('UNKNOWN_VENDOR')

        return {'score': min(score, 100), 'flags': flags}
```

### 5.2 — analysis/device_classifier.py

```python
from datetime import datetime, timedelta

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
```

### 5.3 — analysis/ssid_analyzer.py

```python
import re
from typing import Dict, List

class SSIDAnalyzer:
    """
    Extracts personally identifying information from SSID names.
    Identifies hotspot names, employer names, ISP patterns, etc.
    """

    PERSONAL_HOTSPOT_PATTERNS = [
        (r"^(.+)'s?\s+iphone$", 'person_name', 'IPHONE_HOTSPOT'),
        (r"^(.+)'s?\s+android$", 'person_name', 'ANDROID_HOTSPOT'),
        (r"^(.+)'s?\s+galaxy\b", 'person_name', 'GALAXY_HOTSPOT'),
        (r"^(.+)'s?\s+macbook\b", 'person_name', 'MACBOOK_HOTSPOT'),
        (r"^(.+)'s?\s+ipad\b", 'person_name', 'IPAD_HOTSPOT'),
        (r"^(.+)'s?\s+phone$", 'person_name', 'PHONE_HOTSPOT'),
    ]

    ISP_PATTERNS = [
        ('xfinitywifi', 'Comcast/Xfinity', 'ISP_COMCAST'),
        ('attwifi', 'AT&T', 'ISP_ATT'),
        ('spectrum', 'Charter Spectrum', 'ISP_CHARTER'),
        ('cox-', 'Cox Communications', 'ISP_COX'),
        ('verizon', 'Verizon', 'ISP_VERIZON'),
        ('tmobile', 'T-Mobile', 'ISP_TMOBILE'),
    ]

    def analyze(self, ssid: str) -> Dict:
        result = {
            'ssid': ssid,
            'flags': [],
            'extracted_name': None,
            'isp': None,
            'is_hotspot': False,
            'is_default_router': False,
            'has_address_info': False,
            'risk_intel': []
        }
        if not ssid:
            return result

        ssid_lower = ssid.lower().strip()

        # Personal hotspot detection
        for pattern, data_type, flag in self.PERSONAL_HOTSPOT_PATTERNS:
            match = re.match(pattern, ssid_lower, re.IGNORECASE)
            if match:
                name = match.group(1).strip().title()
                result['extracted_name'] = name
                result['is_hotspot'] = True
                result['flags'].append(flag)
                result['risk_intel'].append(
                    f"Personal hotspot — owner name likely: {name}"
                )

        # ISP detection
        for pattern, isp_name, flag in self.ISP_PATTERNS:
            if pattern in ssid_lower:
                result['isp'] = isp_name
                result['flags'].append(flag)

        # Address/location info in SSID
        if re.search(r'\d{3,5}\s+\w+\s+(st|ave|rd|blvd|ln|dr|ct|way)', ssid_lower):
            result['has_address_info'] = True
            result['flags'].append('ADDRESS_IN_SSID')
            result['risk_intel'].append("SSID may contain a street address")

        # Email in SSID
        if re.search(r'[\w.]+@[\w.]+\.\w+', ssid):
            result['flags'].append('EMAIL_IN_SSID')
            result['risk_intel'].append("SSID appears to contain an email address")

        return result
```

---

## PHASE 6: ENRICHMENT MODULES

### 6.1 — enrichment/oui_lookup.py

```python
import json
import os
from functools import lru_cache

class OUILookup:
    """
    Local IEEE OUI database lookup.
    Bundled oui.json at static/data/oui.json
    No internet required.

    To update: download from https://standards-oui.ieee.org/oui/oui.txt
    and convert to JSON with the included update_oui.py script.
    """

    KNOWN_CAMERA_OUIS = {
        '24:0A:C4': 'Espressif Systems (ESP8266/ESP32)',
        '30:AE:A4': 'Espressif Systems (ESP8266/ESP32)',
        '24:6F:28': 'Espressif Systems (ESP8266/ESP32)',
        '3C:61:05': 'Espressif Systems (ESP8266/ESP32)',
        'D4:5D:64': 'Hikvision Digital Technology',
        'B4:A2:EB': 'Hikvision Digital Technology',
        'BC:32:5F': 'Hikvision Digital Technology',
        'E0:0A:F6': 'Dahua Technology',
        '8C:E7:48': 'Dahua Technology',
        'DC:44:27': 'Reolink Innovation',
        'C8:02:8F': 'Reolink Innovation',
        'E4:AB:89': 'Amcrest Technologies',
    }

    def __init__(self, oui_path: str):
        self.oui_path = oui_path
        self._db = {}
        self._load()

    def _load(self):
        if os.path.exists(self.oui_path):
            try:
                with open(self.oui_path, 'r') as f:
                    self._db = json.load(f)
            except Exception:
                self._db = {}

    @lru_cache(maxsize=4096)
    def lookup(self, mac: str) -> str:
        if not mac:
            return 'Unknown'
        oui = mac.upper()[:8]

        # Check known camera OUIs first
        if oui in self.KNOWN_CAMERA_OUIS:
            return self.KNOWN_CAMERA_OUIS[oui]

        # Check local database
        if oui in self._db:
            return self._db[oui]

        # Try without colons
        oui_clean = oui.replace(':', '')[:6]
        for key, val in self._db.items():
            if key.replace(':', '')[:6] == oui_clean:
                return val

        return 'Unknown'

    def is_camera_vendor(self, mac: str) -> bool:
        return mac.upper()[:8] in self.KNOWN_CAMERA_OUIS

    def is_espressif(self, mac: str) -> bool:
        espressif_ouis = {'24:0A:C4', '30:AE:A4', '24:6F:28', '3C:61:05',
                          'B8:D6:1A', 'CC:50:E3', 'A4:CF:12', '4C:EB:D6'}
        return mac.upper()[:8] in espressif_ouis
```

### 6.2 — enrichment/wigle_lookup.py

```python
import requests
import base64
from typing import Optional, Dict

class WiGLELookup:
    """
    WiGLE.net BSSID geolocation lookup.
    Free account: ~10 queries/day (more with wardriving contributions)
    API docs: https://api.wigle.net/swagger
    """
    BASE_URL = 'https://api.wigle.net/api/v2'

    def __init__(self, api_name: str, api_token: str):
        self.api_name = api_name
        self.api_token = api_token
        self._auth = base64.b64encode(
            f"{api_name}:{api_token}".encode()
        ).decode() if api_name and api_token else None

    def is_configured(self) -> bool:
        return bool(self._auth)

    def lookup_bssid(self, bssid: str) -> Optional[Dict]:
        """Look up a WiFi BSSID to get GPS location history."""
        if not self.is_configured():
            return None
        try:
            resp = requests.get(
                f"{self.BASE_URL}/network/search",
                params={'netid': bssid},
                headers={'Authorization': f'Basic {self._auth}'},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get('results', [])
                if results:
                    r = results[0]
                    return {
                        'bssid': bssid,
                        'ssid': r.get('ssid'),
                        'latitude': r.get('trilat'),
                        'longitude': r.get('trilong'),
                        'first_seen': r.get('firsttime'),
                        'last_seen': r.get('lasttime'),
                        'country': r.get('country'),
                        'city': r.get('city'),
                        'source': 'wigle'
                    }
        except Exception:
            pass
        return None

    def search_ssid(self, ssid: str, lat: float = None, lon: float = None) -> list:
        """Search for all APs broadcasting a given SSID."""
        if not self.is_configured():
            return []
        params = {'ssid': ssid, 'freenet': 'false', 'paynet': 'false'}
        if lat and lon:
            params.update({'latrange1': lat - 0.1, 'latrange2': lat + 0.1,
                           'longrange1': lon - 0.1, 'longrange2': lon + 0.1})
        try:
            resp = requests.get(
                f"{self.BASE_URL}/network/search",
                params=params,
                headers={'Authorization': f'Basic {self._auth}'},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json().get('results', [])
        except Exception:
            pass
        return []
```

### 6.3 — enrichment/nvd_lookup.py

```python
import requests
from typing import List, Dict
from datetime import datetime, timedelta

class NVDLookup:
    """
    NIST National Vulnerability Database CVE lookup.
    Free, no API key required for basic use.
    Rate limit: 5 requests per 30 seconds without key, 50/30s with key.
    """
    BASE_URL = 'https://services.nvd.nist.gov/rest/json/cves/2.0'

    def lookup_vendor(self, vendor_name: str, days_back: int = 90) -> List[Dict]:
        """Get recent CVEs for a vendor/product."""
        if not vendor_name or vendor_name.lower() in ('unknown', ''):
            return []
        try:
            pub_start = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%dT00:00:00.000')
            resp = requests.get(
                self.BASE_URL,
                params={
                    'keywordSearch': vendor_name,
                    'pubStartDate': pub_start,
                    'resultsPerPage': 10
                },
                timeout=15
            )
            if resp.status_code == 200:
                vulns = resp.json().get('vulnerabilities', [])
                return [self._normalize_cve(v) for v in vulns]
        except Exception:
            pass
        return []

    def _normalize_cve(self, vuln: dict) -> dict:
        cve = vuln.get('cve', {})
        metrics = cve.get('metrics', {})
        severity = 'UNKNOWN'
        score = 0.0
        if 'cvssMetricV31' in metrics:
            cvss = metrics['cvssMetricV31'][0].get('cvssData', {})
            severity = cvss.get('baseSeverity', 'UNKNOWN')
            score = cvss.get('baseScore', 0.0)
        elif 'cvssMetricV2' in metrics:
            cvss = metrics['cvssMetricV2'][0].get('cvssData', {})
            severity = 'HIGH' if float(cvss.get('baseScore', 0)) >= 7 else 'MEDIUM'
            score = cvss.get('baseScore', 0.0)
        descs = cve.get('descriptions', [])
        description = next((d['value'] for d in descs if d['lang'] == 'en'), '')
        return {
            'cve_id': cve.get('id'),
            'severity': severity,
            'score': score,
            'description': description[:300],
            'published': cve.get('published', '')[:10],
            'source': 'nvd'
        }
```

---

## PHASE 7: INTEL MODULES

### 7.1 — intel/alert_manager.py

```python
class AlertManager:
    RULES = [
        {'name': 'AIRTAG', 'check': lambda d: d.get('is_airtag'), 'severity': 'critical',
         'title': 'AirTag detected', 'type': 'tracker'},
        {'name': 'OPEN_CAMERA', 'check': lambda d: 'CAMERA_VENDOR_OUI' in d.get('risk_flags', []) and 'OPEN_NETWORK' in d.get('risk_flags', []),
         'severity': 'critical', 'title': 'Open-network camera device detected', 'type': 'camera'},
        {'name': 'NEW_HIGH_RISK', 'check': lambda d: d.get('classification') == 'new' and d.get('risk_score', 0) >= 60,
         'severity': 'high', 'title': 'New high-risk device appeared', 'type': 'new_device'},
        {'name': 'HIDDEN_SSID', 'check': lambda d: d.get('hidden') and d.get('risk_score', 0) >= 40,
         'severity': 'medium', 'title': 'Hidden SSID with elevated risk', 'type': 'hidden_ssid'},
        {'name': 'ESP_DEVICE', 'check': lambda d: 'CAMERA_VENDOR_OUI' in d.get('risk_flags', []),
         'severity': 'medium', 'title': 'ESP32/ESP8266 device detected (potential hidden camera)', 'type': 'iot_device'},
    ]

    def __init__(self, db):
        self.db = db
        self._fired = set()

    def evaluate_wifi(self, device: dict):
        self._evaluate(device, 'wifi')

    def evaluate_ble(self, device: dict):
        self._evaluate(device, 'ble')

    def _evaluate(self, device: dict, scan_type: str):
        mac = device.get('mac', '')
        for rule in self.RULES:
            try:
                if rule['check'](device):
                    key = f"{rule['name']}_{mac}"
                    if key not in self._fired:
                        self._fired.add(key)
                        self.db.log_intel_event(
                            event_type=rule['type'],
                            severity=rule['severity'],
                            title=rule['title'],
                            device_mac=mac,
                            ssid=device.get('ssid'),
                            detail=f"Flags: {device.get('risk_flags')} | Score: {device.get('risk_score')}"
                        )
            except Exception:
                continue
```

### 7.2 — intel/debrief_generator.py

```python
import json
from datetime import datetime
from collections import Counter

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

        # Signal density over time
        scan_times = sorted(set(e['scan_time'][:16] for e in history))
        density_by_minute = Counter(e['scan_time'][:16] for e in history)

        debrief = {
            'generated': datetime.utcnow().isoformat(),
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
                    'flags': json.loads(d.get('risk_flags', '[]')),
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
```

---

## PHASE 8: API ROUTES

### 8.1 — api/scan_routes.py

```python
from flask import Blueprint, jsonify, current_app

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/current', methods=['GET'])
def get_current_scan():
    scanner = current_app.config['SCANNER']
    return jsonify(scanner.get_current_state())

@scan_bp.route('/trigger/wifi', methods=['POST'])
def trigger_wifi():
    scanner = current_app.config['SCANNER']
    import threading
    threading.Thread(target=scanner._run_wifi_scan, daemon=True).start()
    return jsonify({'status': 'triggered', 'type': 'wifi'})

@scan_bp.route('/trigger/ble', methods=['POST'])
def trigger_ble():
    scanner = current_app.config['SCANNER']
    import threading
    threading.Thread(target=scanner._run_ble_scan, daemon=True).start()
    return jsonify({'status': 'triggered', 'type': 'ble'})

@scan_bp.route('/trigger/network', methods=['POST'])
def trigger_network():
    scanner = current_app.config['SCANNER']
    import threading
    threading.Thread(target=scanner._run_network_scan, daemon=True).start()
    return jsonify({'status': 'triggered', 'type': 'network'})
```

### 8.2 — api/device_routes.py

```python
from flask import Blueprint, jsonify, request, current_app

device_bp = Blueprint('devices', __name__)

@device_bp.route('/', methods=['GET'])
def get_devices():
    db = current_app.config['DB']
    device_type = request.args.get('type')
    limit = int(request.args.get('limit', 500))
    devices = db.get_all_devices(device_type=device_type, limit=limit)
    return jsonify({'devices': devices, 'count': len(devices)})

@device_bp.route('/<mac>', methods=['GET'])
def get_device(mac):
    db = current_app.config['DB']
    device_type = request.args.get('type', 'wifi')
    device = db.get_device(mac, device_type)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    return jsonify(device)

@device_bp.route('/<mac>/notes', methods=['POST'])
def update_notes(mac):
    db = current_app.config['DB']
    data = request.get_json()
    device_type = data.get('type', 'wifi')
    notes = data.get('notes', '')
    with db.get_conn() as conn:
        conn.execute(
            "UPDATE devices SET notes=? WHERE mac=? AND device_type=?",
            (notes, mac, device_type)
        )
    return jsonify({'status': 'updated'})
```

### 8.3 — api/intel_routes.py

```python
from flask import Blueprint, jsonify, request, current_app

intel_bp = Blueprint('intel', __name__)

@intel_bp.route('/events', methods=['GET'])
def get_events():
    db = current_app.config['DB']
    limit = int(request.args.get('limit', 100))
    unacked = request.args.get('unacked', 'false').lower() == 'true'
    events = db.get_intel_events(limit=limit, unacked_only=unacked)
    return jsonify({'events': events, 'count': len(events)})

@intel_bp.route('/events/<int:event_id>/ack', methods=['POST'])
def ack_event(event_id):
    db = current_app.config['DB']
    with db.get_conn() as conn:
        conn.execute("UPDATE intel_events SET acknowledged=1 WHERE id=?", (event_id,))
    return jsonify({'status': 'acknowledged'})

@intel_bp.route('/debrief', methods=['GET'])
def get_debrief():
    db = current_app.config['DB']
    from intel.debrief_generator import DebriefGenerator
    window = int(request.args.get('window', 5))
    gen = DebriefGenerator(db)
    debrief = gen.generate(window_minutes=window)
    return jsonify(debrief)
```

### 8.4 — api/enrichment_routes.py

```python
from flask import Blueprint, jsonify, request, current_app

enrichment_bp = Blueprint('enrichment', __name__)

@enrichment_bp.route('/oui/<mac>', methods=['GET'])
def lookup_oui(mac):
    config = current_app.config['ORION_CONFIG']
    from enrichment.oui_lookup import OUILookup
    oui = OUILookup(config.oui_path)
    return jsonify({
        'mac': mac,
        'vendor': oui.lookup(mac),
        'is_camera': oui.is_camera_vendor(mac),
        'is_espressif': oui.is_espressif(mac)
    })

@enrichment_bp.route('/wigle/<bssid>', methods=['GET'])
def lookup_wigle(bssid):
    config = current_app.config['ORION_CONFIG']
    if not config.wigle_api_name:
        return jsonify({'error': 'WiGLE not configured'}), 400
    from enrichment.wigle_lookup import WiGLELookup
    wigle = WiGLELookup(config.wigle_api_name, config.wigle_api_token)
    result = wigle.lookup_bssid(bssid)
    return jsonify(result or {'error': 'Not found'})

@enrichment_bp.route('/cve/<vendor>', methods=['GET'])
def lookup_cve(vendor):
    from enrichment.nvd_lookup import NVDLookup
    nvd = NVDLookup()
    cves = nvd.lookup_vendor(vendor)
    return jsonify({'vendor': vendor, 'cves': cves, 'count': len(cves)})

@enrichment_bp.route('/ssid', methods=['POST'])
def analyze_ssid():
    data = request.get_json()
    ssid = data.get('ssid', '')
    from analysis.ssid_analyzer import SSIDAnalyzer
    analyzer = SSIDAnalyzer()
    return jsonify(analyzer.analyze(ssid))
```

### 8.5 — api/ui_routes.py

```python
from flask import Blueprint, render_template, current_app

ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/')
@ui_bp.route('/hud')
def hud():
    return render_template('hud.html')

@ui_bp.route('/timeline')
def timeline():
    return render_template('timeline.html')

@ui_bp.route('/devices')
def devices():
    return render_template('devices.html')

@ui_bp.route('/enrichment')
def enrichment():
    return render_template('enrichment.html')

@ui_bp.route('/settings')
def settings():
    return render_template('settings.html')

@ui_bp.route('/alerts')
def alerts():
    return render_template('alerts.html')

@ui_bp.route('/debrief')
def debrief():
    return render_template('debrief.html')
```

---

## PHASE 9: FRONTEND — ALL SCREENS

### CSS DESIGN SYSTEM

File: `static/css/base.css`

```css
/* ============================================
   ORION — Design System
   Dark tactical HUD aesthetic
   Color palette: deep black + electric blue + amber alerts
   ============================================ */

:root {
  /* Core palette */
  --bg-primary:    #050a0f;
  --bg-secondary:  #0a1520;
  --bg-card:       #0d1e2e;
  --bg-elevated:   #112233;

  /* Brand */
  --accent-blue:   #00aaff;
  --accent-cyan:   #00ffee;
  --accent-dim:    #004466;

  /* Status */
  --status-ok:     #00cc66;
  --status-warn:   #ffaa00;
  --status-alert:  #ff4444;
  --status-info:   #44aaff;
  --status-new:    #aa44ff;

  /* Text */
  --text-primary:  #e0f0ff;
  --text-secondary:#7aa8cc;
  --text-muted:    #445566;
  --text-label:    #00aaff;

  /* Borders */
  --border:        #1a3a5a;
  --border-bright: #00aaff44;

  /* Typography */
  --font-mono:     'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  --font-ui:       'Inter', 'Segoe UI', system-ui, sans-serif;

  /* Sizing */
  --nav-height:    52px;
  --card-radius:   6px;
  --transition:    0.15s ease;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-ui);
  font-size: 14px;
  line-height: 1.5;
  height: 100%;
  overflow-x: hidden;
}

/* --- Navigation --- */
.nav {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: var(--nav-height);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 16px;
  z-index: 1000;
  gap: 4px;
}

.nav-brand {
  font-family: var(--font-mono);
  font-size: 16px;
  font-weight: 700;
  color: var(--accent-blue);
  letter-spacing: 3px;
  margin-right: 24px;
  text-decoration: none;
}

.nav-brand span { color: var(--accent-cyan); }

.nav-link {
  padding: 6px 12px;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 4px;
  font-size: 12px;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: var(--transition);
}

.nav-link:hover, .nav-link.active {
  color: var(--accent-blue);
  background: var(--accent-dim);
}

.nav-status {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--status-ok);
  box-shadow: 0 0 8px var(--status-ok);
  animation: pulse 2s infinite;
}

.status-dot.offline { background: var(--status-alert); box-shadow: 0 0 8px var(--status-alert); animation: none; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.stat-chip {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-secondary);
  background: var(--bg-card);
  border: 1px solid var(--border);
  padding: 3px 8px;
  border-radius: 12px;
}

.stat-chip span { color: var(--accent-cyan); font-weight: 700; }

/* --- Main layout --- */
.main {
  padding-top: calc(var(--nav-height) + 16px);
  padding-bottom: 24px;
  min-height: 100vh;
}

/* --- Cards --- */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
  padding: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--text-label);
}

/* --- Risk badges --- */
.risk-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
}

.risk-critical { background: #ff000033; color: var(--status-alert); border: 1px solid var(--status-alert); }
.risk-high     { background: #ff440022; color: #ff6644; border: 1px solid #ff6644; }
.risk-medium   { background: #ffaa0022; color: var(--status-warn); border: 1px solid var(--status-warn); }
.risk-low      { background: #00cc6622; color: var(--status-ok); border: 1px solid var(--status-ok); }
.risk-new      { background: #aa44ff22; color: var(--status-new); border: 1px solid var(--status-new); }

/* --- Buttons --- */
.btn {
  padding: 7px 14px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: 12px;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  transition: var(--transition);
  font-family: var(--font-mono);
}

.btn:hover { color: var(--accent-blue); border-color: var(--accent-blue); background: var(--accent-dim); }
.btn-primary { background: var(--accent-dim); color: var(--accent-blue); border-color: var(--accent-blue); }
.btn-primary:hover { background: var(--accent-blue); color: var(--bg-primary); }
.btn-danger { border-color: var(--status-alert); color: var(--status-alert); }

/* --- Tables --- */
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }

.data-table th {
  background: var(--bg-secondary);
  color: var(--text-label);
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
}

.data-table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.data-table tr:hover td { background: var(--bg-elevated); cursor: pointer; }
.data-table .mac-cell { color: var(--accent-cyan); font-size: 11px; }
.data-table .rssi-cell { color: var(--text-secondary); }
.data-table .vendor-cell { color: var(--text-secondary); font-size: 11px; }

/* --- Scrollbar --- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--accent-dim); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-blue); }

/* --- Alert banner --- */
.alert-banner {
  position: fixed;
  top: var(--nav-height);
  left: 0; right: 0;
  background: #ff000022;
  border-bottom: 1px solid var(--status-alert);
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 999;
  font-size: 12px;
  color: var(--status-alert);
  font-family: var(--font-mono);
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from { transform: translateY(-100%); }
  to   { transform: translateY(0); }
}

/* --- Mono values --- */
.mono { font-family: var(--font-mono); }
.dim  { color: var(--text-muted); }
.label { color: var(--text-label); font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
```

### SCREEN 1: HUD RADAR (hud.html + hud.css)

```html
<!-- templates/hud.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ORION — HUD</title>
  <link rel="stylesheet" href="/static/css/base.css">
  <link rel="stylesheet" href="/static/css/hud.css">
</head>
<body>
  <nav class="nav">
    <a href="/" class="nav-brand">ORI<span>ON</span></a>
    <a href="/hud" class="nav-link active">HUD</a>
    <a href="/timeline" class="nav-link">Timeline</a>
    <a href="/devices" class="nav-link">Devices</a>
    <a href="/enrichment" class="nav-link">Intel</a>
    <a href="/debrief" class="nav-link">Debrief</a>
    <a href="/settings" class="nav-link">Config</a>
    <div class="nav-status">
      <span class="status-dot" id="scan-indicator"></span>
      <span class="stat-chip">WiFi <span id="wifi-count">—</span></span>
      <span class="stat-chip">BLE <span id="ble-count">—</span></span>
      <span class="stat-chip">Net <span id="net-count">—</span></span>
    </div>
  </nav>

  <div id="alert-container"></div>

  <main class="main hud-main">
    <!-- Radar Panel -->
    <div class="hud-radar-panel">
      <div class="card">
        <div class="card-header">
          <span class="card-title">Signal Radar</span>
          <div style="display:flex;gap:8px;align-items:center;">
            <button class="btn btn-primary" onclick="triggerScan('wifi')">Scan WiFi</button>
            <button class="btn" onclick="triggerScan('ble')">Scan BLE</button>
          </div>
        </div>
        <div class="radar-container">
          <canvas id="radar-canvas" width="500" height="500"></canvas>
          <div class="radar-overlay">
            <div class="radar-range" data-range="10m">10m</div>
            <div class="radar-range" data-range="25m">25m</div>
            <div class="radar-range" data-range="50m+">50m+</div>
          </div>
        </div>
        <div class="radar-legend">
          <span class="legend-dot wifi"></span> WiFi
          <span class="legend-dot ble"></span> BLE
          <span class="legend-dot network"></span> Network
          <span class="legend-dot alert"></span> Alert
        </div>
      </div>
    </div>

    <!-- Live Device List -->
    <div class="hud-side-panel">
      <!-- Stats row -->
      <div class="hud-stats-row">
        <div class="hud-stat-box">
          <div class="hud-stat-value" id="stat-total">0</div>
          <div class="hud-stat-label">TOTAL</div>
        </div>
        <div class="hud-stat-box alert">
          <div class="hud-stat-value" id="stat-alerts">0</div>
          <div class="hud-stat-label">ALERTS</div>
        </div>
        <div class="hud-stat-box">
          <div class="hud-stat-value" id="stat-new">0</div>
          <div class="hud-stat-label">NEW</div>
        </div>
        <div class="hud-stat-box">
          <div class="hud-stat-value" id="stat-static">0</div>
          <div class="hud-stat-label">STATIC</div>
        </div>
      </div>

      <!-- Live feed -->
      <div class="card" style="flex:1;overflow:hidden;display:flex;flex-direction:column;">
        <div class="card-header">
          <span class="card-title">Live Devices</span>
          <span class="label" id="last-scan-time">—</span>
        </div>
        <div id="live-device-list" class="live-feed"></div>
      </div>

      <!-- Alert feed -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">Recent Intel</span>
          <a href="/timeline" class="label" style="text-decoration:none;">View All</a>
        </div>
        <div id="intel-feed" class="intel-feed"></div>
      </div>
    </div>
  </main>

  <script src="/static/js/api.js"></script>
  <script src="/static/js/radar.js"></script>
  <script src="/static/js/alerts.js"></script>
  <script src="/static/js/app.js"></script>
</body>
</html>
```

```css
/* static/css/hud.css */
.hud-main {
  display: grid;
  grid-template-columns: 540px 1fr;
  gap: 12px;
  padding: calc(var(--nav-height) + 16px) 16px 16px;
  height: 100vh;
  overflow: hidden;
}

.hud-radar-panel { display: flex; flex-direction: column; }

.radar-container {
  position: relative;
  width: 500px;
  height: 500px;
  margin: 0 auto;
}

#radar-canvas {
  display: block;
  border-radius: 50%;
  border: 1px solid var(--border-bright);
  box-shadow: 0 0 30px #00aaff11 inset, 0 0 2px var(--accent-blue);
}

.radar-legend {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 8px;
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.legend-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
}

.legend-dot.wifi    { background: var(--accent-blue); box-shadow: 0 0 6px var(--accent-blue); }
.legend-dot.ble     { background: var(--accent-cyan); box-shadow: 0 0 6px var(--accent-cyan); }
.legend-dot.network { background: var(--status-ok);   box-shadow: 0 0 6px var(--status-ok); }
.legend-dot.alert   { background: var(--status-alert); box-shadow: 0 0 6px var(--status-alert); }

.hud-side-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: hidden;
}

.hud-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.hud-stat-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
  padding: 12px;
  text-align: center;
}

.hud-stat-box.alert { border-color: var(--status-alert); }

.hud-stat-value {
  font-family: var(--font-mono);
  font-size: 28px;
  font-weight: 700;
  color: var(--accent-blue);
  line-height: 1;
}

.hud-stat-box.alert .hud-stat-value { color: var(--status-alert); }

.hud-stat-label {
  font-size: 10px;
  letter-spacing: 2px;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-top: 4px;
}

.live-feed {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.device-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: var(--transition);
  border-left: 2px solid transparent;
}

.device-row:hover { background: var(--bg-elevated); }
.device-row.risk-high   { border-left-color: var(--status-alert); }
.device-row.risk-medium { border-left-color: var(--status-warn); }
.device-row.risk-new    { border-left-color: var(--status-new); }

.device-row-icon {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: var(--accent-dim);
  display: flex; align-items: center; justify-content: center;
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--accent-blue);
  flex-shrink: 0;
}

.device-row-info { flex: 1; min-width: 0; }

.device-row-ssid {
  font-size: 13px;
  color: var(--text-primary);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.device-row-meta {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  display: flex;
  gap: 8px;
  margin-top: 2px;
}

.device-row-score {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  min-width: 28px;
  text-align: right;
}

.score-ok     { color: var(--status-ok); }
.score-warn   { color: var(--status-warn); }
.score-alert  { color: var(--status-alert); }

.intel-feed { max-height: 180px; overflow-y: auto; }

.intel-event {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 4px;
  border-bottom: 1px solid var(--border);
  font-size: 11px;
}

.intel-sev {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 1px;
  padding: 2px 6px;
  border-radius: 2px;
  flex-shrink: 0;
  text-transform: uppercase;
}

.sev-critical { background: #ff000033; color: var(--status-alert); }
.sev-high     { background: #ff440022; color: #ff6644; }
.sev-medium   { background: #ffaa0022; color: var(--status-warn); }
.sev-info     { background: #44aaff22; color: var(--status-info); }

.intel-title { color: var(--text-primary); flex: 1; }
.intel-time  { color: var(--text-muted); font-size: 10px; white-space: nowrap; }

@media (max-width: 1100px) {
  .hud-main { grid-template-columns: 1fr; height: auto; overflow: visible; }
  .radar-container { width: 100%; }
  #radar-canvas { width: 100% !important; height: auto !important; }
}
```

### RADAR JS (static/js/radar.js)

```javascript
// static/js/radar.js
// Canvas-based tactical radar renderer

const RadarCanvas = {
  canvas: null,
  ctx: null,
  centerX: 250,
  centerY: 250,
  radius: 240,
  sweepAngle: 0,
  devices: [],
  dots: [],

  init(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.centerX = this.canvas.width / 2;
    this.centerY = this.canvas.height / 2;
    this.radius = (this.canvas.width / 2) - 10;
    this._startSweep();
  },

  setDevices(devices) {
    this.devices = devices;
    this._buildDots();
  },

  _buildDots() {
    this.dots = this.devices.map(d => {
      const dist = d.distance_m || 15;
      const maxDist = 60;
      const r = Math.min((dist / maxDist) * this.radius, this.radius - 10);
      const angle = this._macToAngle(d.mac || '');
      const jitter = ((d.rssi || -70) % 10) * 2;
      return {
        x: this.centerX + r * Math.cos(angle + jitter * 0.01),
        y: this.centerY + r * Math.sin(angle + jitter * 0.01),
        color: this._riskColor(d.risk_score || 0, d.device_type || 'wifi'),
        label: (d.ssid || d.name || d.mac || '').substring(0, 16),
        risk_score: d.risk_score || 0,
        type: d.device_type || 'wifi'
      };
    });
  },

  _macToAngle(mac) {
    let hash = 0;
    for (let i = 0; i < mac.length; i++) {
      hash = mac.charCodeAt(i) + ((hash << 5) - hash);
    }
    return (hash % 628) / 100; // 0 to 2π
  },

  _riskColor(score, type) {
    if (score >= 70) return '#ff4444';
    if (score >= 40) return '#ffaa00';
    if (type === 'ble') return '#00ffee';
    if (type === 'network') return '#00cc66';
    return '#00aaff';
  },

  _startSweep() {
    const draw = () => {
      this._drawFrame();
      this.sweepAngle = (this.sweepAngle + 0.015) % (Math.PI * 2);
      requestAnimationFrame(draw);
    };
    draw();
  },

  _drawFrame() {
    const ctx = this.ctx;
    const cx = this.centerX;
    const cy = this.centerY;
    const r = this.radius;

    // Background
    ctx.fillStyle = '#050a0f';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Clip to circle
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.clip();

    // Grid rings
    [0.25, 0.5, 0.75, 1.0].forEach(frac => {
      ctx.beginPath();
      ctx.arc(cx, cy, r * frac, 0, Math.PI * 2);
      ctx.strokeStyle = '#1a3a5a';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // Crosshairs
    ctx.strokeStyle = '#1a3a5a';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(cx - r, cy); ctx.lineTo(cx + r, cy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx, cy - r); ctx.lineTo(cx, cy + r); ctx.stroke();

    // Sweep gradient
    const sweep = ctx.createConicalGradient ? null : null;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this.sweepAngle);
    const grad = ctx.createLinearGradient(0, 0, r, 0);
    grad.addColorStop(0, 'rgba(0, 170, 255, 0.4)');
    grad.addColorStop(0.3, 'rgba(0, 170, 255, 0.1)');
    grad.addColorStop(1, 'rgba(0, 170, 255, 0)');
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, r, -0.3, 0);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.restore();

    // Sweep line
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this.sweepAngle);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(r, 0);
    ctx.strokeStyle = 'rgba(0, 170, 255, 0.8)';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.restore();

    // Device dots
    this.dots.forEach(dot => {
      // Glow
      const glow = ctx.createRadialGradient(dot.x, dot.y, 0, dot.x, dot.y, 12);
      glow.addColorStop(0, dot.color + '88');
      glow.addColorStop(1, 'transparent');
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, 12, 0, Math.PI * 2);
      ctx.fillStyle = glow;
      ctx.fill();

      // Core dot
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, dot.risk_score >= 60 ? 5 : 3, 0, Math.PI * 2);
      ctx.fillStyle = dot.color;
      ctx.fill();

      // Label
      ctx.fillStyle = dot.color;
      ctx.font = '9px JetBrains Mono, monospace';
      ctx.fillText(dot.label, dot.x + 7, dot.y - 4);
    });

    // Center dot (scanner)
    ctx.beginPath();
    ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#00ffee';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(cx, cy, 10, 0, Math.PI * 2);
    ctx.strokeStyle = '#00ffee44';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.restore(); // end clip
  }
};
```

### APP BOOTSTRAP JS (static/js/app.js)

```javascript
// static/js/app.js
const POLL_INTERVAL = 5000; // ms

async function loadHUD() {
  try {
    const state = await OrionAPI.getCurrentScan();
    const allDevices = await OrionAPI.getDevices();
    const intel = await OrionAPI.getIntelEvents(10);

    // Counts
    document.getElementById('wifi-count').textContent = state.wifi_count || 0;
    document.getElementById('ble-count').textContent = state.ble_count || 0;
    document.getElementById('net-count').textContent = state.network_count || 0;

    // Stats
    const allDevList = allDevices.devices || [];
    const alertDevs = allDevList.filter(d => d.risk_score >= 60);
    const newDevs = allDevList.filter(d => d.classification === 'new');
    const staticDevs = allDevList.filter(d => d.classification === 'static');

    document.getElementById('stat-total').textContent = allDevList.length;
    document.getElementById('stat-alerts').textContent = alertDevs.length;
    document.getElementById('stat-new').textContent = newDevs.length;
    document.getElementById('stat-static').textContent = staticDevs.length;

    // Radar
    const radarDevs = [
      ...state.wifi.map(d => ({ ...d, device_type: 'wifi' })),
      ...state.ble.map(d => ({ ...d, device_type: 'ble' })),
      ...state.network.map(d => ({ ...d, device_type: 'network' }))
    ];
    if (window.RadarCanvas) RadarCanvas.setDevices(radarDevs);

    // Live device list
    renderLiveDevices(allDevList.slice(0, 30));

    // Intel feed
    renderIntelFeed(intel.events || []);

    // Alert banners
    const criticalAlerts = (intel.events || []).filter(
      e => e.severity === 'critical' && !e.acknowledged
    );
    if (criticalAlerts.length > 0) {
      showAlertBanner(criticalAlerts[0]);
    }

    document.getElementById('last-scan-time').textContent =
      new Date().toLocaleTimeString();

  } catch (err) {
    document.getElementById('scan-indicator').classList.add('offline');
    console.error('HUD load error:', err);
  }
}

function renderLiveDevices(devices) {
  const container = document.getElementById('live-device-list');
  if (!container) return;
  container.innerHTML = devices.map(d => {
    const score = d.risk_score || 0;
    const riskClass = score >= 70 ? 'risk-high' : score >= 40 ? 'risk-medium' :
                      d.classification === 'new' ? 'risk-new' : '';
    const scoreClass = score >= 70 ? 'score-alert' : score >= 40 ? 'score-warn' : 'score-ok';
    const typeLabel = { wifi: 'WF', ble: 'BT', network: 'LAN' }[d.device_type] || 'UK';
    const name = d.ssid || d.name || d.mac || 'Unknown';
    return `
      <div class="device-row ${riskClass}" onclick="window.location='/devices'">
        <div class="device-row-icon">${typeLabel}</div>
        <div class="device-row-info">
          <div class="device-row-ssid">${escHtml(name)}</div>
          <div class="device-row-meta">
            <span>${escHtml(d.vendor || 'Unknown')}</span>
            <span>${d.rssi ? d.rssi + 'dBm' : ''}</span>
            <span class="mono">${escHtml((d.mac || '').substring(0, 8))}</span>
          </div>
        </div>
        <div class="device-row-score ${scoreClass}">${score}</div>
      </div>`;
  }).join('');
}

function renderIntelFeed(events) {
  const container = document.getElementById('intel-feed');
  if (!container) return;
  container.innerHTML = events.slice(0, 10).map(e => `
    <div class="intel-event">
      <span class="intel-sev sev-${e.severity}">${e.severity}</span>
      <span class="intel-title">${escHtml(e.title)}</span>
      <span class="intel-time">${formatTime(e.event_time)}</span>
    </div>`).join('');
}

function showAlertBanner(event) {
  const container = document.getElementById('alert-container');
  if (!container) return;
  container.innerHTML = `
    <div class="alert-banner">
      ⚠ ${escHtml(event.title)}
      <button class="btn btn-danger" onclick="ackAlert(${event.id})" style="margin-left:auto;">
        Acknowledge
      </button>
    </div>`;
}

async function ackAlert(id) {
  await OrionAPI.ackIntelEvent(id);
  document.getElementById('alert-container').innerHTML = '';
}

async function triggerScan(type) {
  await OrionAPI.triggerScan(type);
  setTimeout(loadHUD, 2000);
}

function escHtml(s) {
  return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

function formatTime(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('radar-canvas')) {
    RadarCanvas.init('radar-canvas');
  }
  loadHUD();
  setInterval(loadHUD, POLL_INTERVAL);
});
```

### API CLIENT JS (static/js/api.js)

```javascript
// static/js/api.js
const OrionAPI = {
  async _fetch(path, options = {}) {
    const resp = await fetch(path, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    if (!resp.ok) throw new Error(`API error: ${resp.status}`);
    return resp.json();
  },

  getCurrentScan:     ()     => OrionAPI._fetch('/api/scan/current'),
  getDevices:         (type) => OrionAPI._fetch(`/api/devices/${type ? '?type=' + type : ''}`),
  getDevice:          (mac, type) => OrionAPI._fetch(`/api/devices/${mac}?type=${type || 'wifi'}`),
  getIntelEvents:     (limit) => OrionAPI._fetch(`/api/intel/events?limit=${limit || 50}`),
  getDebrief:         (window) => OrionAPI._fetch(`/api/intel/debrief?window=${window || 5}`),
  ackIntelEvent:      (id)   => OrionAPI._fetch(`/api/intel/events/${id}/ack`, { method: 'POST' }),
  triggerScan:        (type) => OrionAPI._fetch(`/api/scan/trigger/${type}`, { method: 'POST' }),
  lookupOUI:          (mac)  => OrionAPI._fetch(`/api/enrich/oui/${mac}`),
  lookupWiGLE:        (bssid) => OrionAPI._fetch(`/api/enrich/wigle/${bssid}`),
  lookupCVE:          (vendor) => OrionAPI._fetch(`/api/enrich/cve/${encodeURIComponent(vendor)}`),
  analyzeSSID:        (ssid) => OrionAPI._fetch('/api/enrich/ssid', { method: 'POST', body: JSON.stringify({ ssid }) }),
};
```

---

## PHASE 10: INSTALLER SCRIPTS

### install.sh (Linux / Android / Pi)

```bash
#!/bin/bash
# ORION Installer — Linux / Termux / Raspberry Pi
set -e

ORION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "=============================="
echo " ORION Signal Intelligence"
echo " Installer v1.0.0"
echo "=============================="

# Detect platform
if [ -n "$PREFIX" ] && echo "$PREFIX" | grep -q "com.termux"; then
  PLATFORM="termux"
  PKG_CMD="pkg"
  PIP_CMD="pip"
  echo "[Platform] Android / Termux"
elif [ -f /proc/device-tree/model ] && grep -q "Raspberry" /proc/device-tree/model; then
  PLATFORM="raspberrypi"
  PKG_CMD="sudo apt-get"
  PIP_CMD="pip3"
  echo "[Platform] Raspberry Pi"
else
  PLATFORM="linux"
  PKG_CMD="sudo apt-get"
  PIP_CMD="pip3"
  echo "[Platform] Linux"
fi

# Install system dependencies
if [ "$PLATFORM" == "termux" ]; then
  echo "[+] Updating Termux packages..."
  pkg update -y
  pkg install -y python nmap git termux-api
  termux-setup-storage 2>/dev/null || true
else
  echo "[+] Installing system dependencies..."
  $PKG_CMD update -y
  $PKG_CMD install -y python3 python3-pip nmap bluetooth bluez git
fi

# Install Python dependencies
echo "[+] Installing Python dependencies..."
cd "$ORION_DIR"
$PIP_CMD install --break-system-packages -r requirements.txt 2>/dev/null || \
$PIP_CMD install -r requirements.txt

# Create data directories
mkdir -p "$ORION_DIR/data/logs"
chmod 755 "$ORION_DIR/data"

# Create default .env if it doesn't exist
if [ ! -f "$ORION_DIR/.env" ]; then
  cp "$ORION_DIR/.env.example" "$ORION_DIR/.env" 2>/dev/null || \
  cat > "$ORION_DIR/.env" << 'EOF'
ORION_HOST=127.0.0.1
ORION_PORT=5000
ORION_DEBUG=false
ENABLE_WIFI=true
ENABLE_BLE=true
ENABLE_NETWORK=true
ENABLE_ENRICHMENT=false
EOF
fi

# Create launcher alias
if [ "$PLATFORM" == "termux" ]; then
  echo 'alias orion="cd '"$ORION_DIR"' && python orion.py"' >> ~/.bashrc
fi

echo ""
echo "=============================="
echo " ORION installed successfully"
echo " Run: python $ORION_DIR/orion.py"
echo " Then open: http://127.0.0.1:5000"
echo "=============================="
```

### run.bat (Windows)

```batch
@echo off
title ORION — Signal Intelligence
cd /d C:\Projects\orion

if not exist "data" mkdir data
if not exist "data\logs" mkdir data\logs

echo ==============================
echo  ORION Signal Intelligence
echo  Starting server...
echo ==============================
echo.
echo Open browser: http://127.0.0.1:5000
echo Press Ctrl+C to stop
echo.

python orion.py
pause
```

### run.sh (Linux/Pi/Termux)

```bash
#!/bin/bash
cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p data/logs
echo "==============================="
echo " ORION — Starting server..."
echo " Open: http://127.0.0.1:5000"
echo " Ctrl+C to stop"
echo "==============================="
python orion.py
```

---

## PHASE 11: GITHUB PUSH SEQUENCE

After all files are created, Claude executes:

```bash
cd C:\Projects\orion
git add .
git commit -m "feat: initial ORION v1.0.0 — WiFi/BLE/Network scanner + HUD"
git branch -M main
git push -u origin main
```

Subsequent commits should follow this pattern:
```
feat: add WiGLE geolocation enrichment
feat: add NVD CVE lookup for detected vendors
feat: add SSID identity analyzer
fix: Termux BLE scanner fallback
chore: update OUI database
```

---

## PHASE 12: DEPLOYMENT & TESTING

### Local dev test (Windows):

```bash
cd C:\Projects\orion
pip install -r requirements.txt
pip install -r requirements-dev.txt
python orion.py
# Open http://127.0.0.1:5000
# WiFi/BLE will use mock data on Windows — real scanning needs Termux/Linux
```

### Run tests:

```bash
cd C:\Projects\orion
pytest tests/ -v --tb=short
pytest tests/test_wifi_scanner.py -v
pytest tests/test_risk_scorer.py -v
```

### Termux (Android) deployment:

```bash
# On the Android device in Termux:
pkg install git python nmap termux-api
git clone https://github.com/YOUR_USERNAME/orion.git ~/orion
cd ~/orion
bash install.sh
python orion.py &
# Open Chrome on phone → http://127.0.0.1:5000
```

### Raspberry Pi deployment:

```bash
git clone https://github.com/YOUR_USERNAME/orion.git ~/orion
cd ~/orion
bash install.sh
sudo python orion.py  # sudo needed for nmap OS detection (optional)
# Access from any device on LAN: http://[PI_IP]:5000
# To expose beyond localhost, change ORION_HOST=0.0.0.0 in .env
```

---

## PHASE 13: DATA FILES TO BUNDLE

### static/data/camera_ouis.txt
One OUI per line, format AA:BB:CC — MAC prefixes for known camera/IoT vendors.
Claude must generate this file from the KNOWN_CAMERA_OUIS dict in risk_scorer.py.

### static/data/evil_ssids.txt
SSID substrings that indicate suspicious networks. One pattern per line.
Claude generates from the SUSPICIOUS_SSID_PATTERNS list.

### static/data/bt_uuids.json
Bluetooth SIG GATT Service UUID registry. Claude generates a compact JSON:
```json
{
  "0x180F": "Battery Service",
  "0x180D": "Heart Rate",
  "0x181C": "User Data",
  "0xFEAA": "Eddystone Beacon",
  ...
}
```

### static/data/oui.json
IEEE OUI lookup database. This is large (~5MB full). Claude generates a MINIMAL
seeded version with the top 500 most common vendor entries. Include full instructions
in README for user to download and replace with the full IEEE database.

---

## PHASE 14: README.md

The README must include:
1. Project description and screenshots placeholder
2. Feature list (all capabilities documented)
3. Platform support matrix table (Android/Pi/Linux/Windows-dev)
4. Quick install instructions for each platform
5. API documentation table (all endpoints)
6. Configuration reference (.env keys)
7. Enrichment setup (WiGLE, Shodan, NVD — all optional)
8. Contributing guidelines
9. Legal/ethical use statement
10. MIT License reference

---

## BUILD ORDER FOR CLAUDE

Execute phases in this exact order. Verify each phase compiles/runs before proceeding.

1. Create directory structure (Phase 1)
2. Write requirements.txt files
3. Write core/ modules (config, database, logger, app)
4. Write scanners/ modules (wifi, ble, network, manager)
5. Write analysis/ modules (risk_scorer, classifier, ssid_analyzer)
6. Write enrichment/ modules (oui_lookup, wigle, nvd)
7. Write intel/ modules (alert_manager, timeline, debrief_generator)
8. Write api/ routes (all blueprints + ui_routes)
9. Write static/css/ files (base, hud, timeline, devices, enrichment, settings)
10. Write templates/ HTML files (all 8 screens)
11. Write static/js/ files (api, radar, app, timeline, devices)
12. Generate static/data/ bundle files
13. Write install.sh, run.bat, run.sh
14. Write tests/ suite
15. Write README.md
16. Git init + push to GitHub (Phase 0.2 + Phase 11)
17. Test locally: `python orion.py` → verify http://127.0.0.1:5000 renders
18. Run pytest and fix any failures

---

## SCREEN INVENTORY (complete list)

| Screen       | Route       | File              | Key Components                                      |
|--------------|-------------|-------------------|-----------------------------------------------------|
| HUD Radar    | /hud        | hud.html          | Canvas radar, live device feed, stats row, alert feed |
| Intel Timeline| /timeline  | timeline.html     | Scrollable event log, severity filters, ack buttons |
| Device Inventory| /devices | devices.html      | Filterable table, search, type tabs, sort by risk   |
| OSINT Intel  | /enrichment | enrichment.html   | BSSID lookup, OUI detail, CVE panel, SSID analyzer  |
| Debrief      | /debrief    | debrief.html      | 5min window summary, AI prompt copy, export JSON    |
| Alerts       | /alerts     | alerts.html       | Active alert list, rules config, history            |
| Settings     | /settings   | settings.html     | API keys, scan intervals, feature toggles, platform |

---

*End of ORION Build Specification v1.0.0*
