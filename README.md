# ORION — Open Source Passive Signal Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-47%20passing-brightgreen.svg)](#testing)
[![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Pi%20%7C%20Linux-blue.svg)](#platform-support)

**WiFi + BLE + Network scanning | OSINT enrichment | Tactical HUD**

ORION is a passive signal intelligence tool that scans for WiFi networks, Bluetooth Low Energy (BLE) devices, and LAN hosts. It scores devices for risk, detects potential surveillance hardware (hidden cameras, AirTags, rogue APs), and presents everything through a tactical radar HUD in your browser.

Built for **Android (Termux)**, **Raspberry Pi**, and **Linux**. Windows supported for development.

---

## Screenshots

| HUD Radar | Device Inventory |
|:---------:|:----------------:|
| ![HUD Radar](docs/shot1.png) | ![Devices](docs/shot2.png) |

| OSINT Enrichment | Signal Debrief |
|:----------------:|:--------------:|
| ![Enrichment](docs/shot3.png) | ![Debrief](docs/shot4.png) |

| Settings |
|:--------:|
| ![Settings](docs/shot5.png) |

---

## Features

- **WiFi Scanner** — Detects all nearby access points with SSID, BSSID, signal strength, channel, security, and estimated distance
- **BLE Scanner** — Discovers Bluetooth LE devices, fingerprints Apple/AirTag/Android/Windows devices, detects trackers
- **Network Scanner** — Passive ARP + optional nmap sweep to map LAN devices
- **Risk Scoring** — 0-100 risk score per device based on OUI, security, SSID patterns, signal strength, and behavior
- **Device Classification** — Categorizes devices as new, transient, recurring, static, mobile, or baseline
- **SSID Analyzer** — Extracts personal names from hotspot SSIDs, detects ISPs, addresses, and email patterns
- **AirTag Detection** — Identifies Apple AirTags and FindMy accessories via BLE manufacturer data
- **Camera Vendor Detection** — Flags Hikvision, Dahua, Reolink, Amcrest, and Espressif (ESP32) devices
- **OSINT Enrichment** — Optional WiGLE geolocation, Shodan, NVD CVE lookup, macaddress.io vendor details
- **Tactical Radar HUD** — Canvas-based radar with live device dots, sweep animation, color-coded risk
- **Intel Timeline** — Scrollable event log with severity filters and acknowledgment
- **Signal Debrief** — AI-ready summary prompt for environment analysis
- **Alert System** — Real-time alerts for AirTags, open cameras, high-risk new devices
- **API Key Auth** — Optional header-based API key authentication for programmatic access
- **Rate Limiting** — Built-in per-IP rate limiting on all API endpoints
- **Zero Cloud Dependencies** — Runs entirely offline; enrichment APIs are optional

---

## Platform Support

| Platform | WiFi | BLE | Network | Notes |
|----------|------|-----|---------|-------|
| Android (Termux) | termux-wifi-scaninfo | bluetoothctl / unofficial API | arp | Primary mobile platform |
| Raspberry Pi | nmcli / iwlist | bleak (BlueZ) | arp + nmap | Full feature support |
| Linux | nmcli / iwlist | bleak (BlueZ) | arp + nmap | Full feature support |
| Windows | netsh (limited) | bleak (WinRT) | arp | Dev/testing only; mock fallback |

---

## Quick Install

### Termux (Android)
```bash
pkg install git python nmap termux-api
git clone https://github.com/Chemtron/orion.git ~/orion
cd ~/orion
bash install.sh
python orion.py
# Open Chrome: http://127.0.0.1:5000
```

### Raspberry Pi / Linux
```bash
git clone https://github.com/Chemtron/orion.git ~/orion
cd ~/orion
bash install.sh
python3 orion.py
# Access from LAN: http://[PI_IP]:5000
```

### Windows (Development)
```bash
cd C:\Projects\orion
pip install -r requirements.txt
python orion.py
# Open browser: http://127.0.0.1:5000
```

---

## Project Structure

```
orion/
├── orion.py                 # Entry point
├── core/                    # App factory, config, database, logging, auth, cache
├── scanners/                # WiFi, BLE, network scanners + manager
├── analysis/                # Risk scoring, device classification, SSID analysis
├── enrichment/              # OUI, WiGLE, Shodan, NVD, macaddress.io lookups
├── intel/                   # Alerts, timeline, debrief, reports
├── api/                     # Flask REST API routes
├── static/
│   ├── css/                 # Dark tactical HUD theme (7 files)
│   ├── js/                  # Vanilla JS controllers (9 files)
│   └── data/                # Bundled OUI database, BT UUIDs, threat lists
├── templates/               # Jinja2 HTML templates (8 screens)
├── tests/                   # pytest suite (47 tests)
├── data/                    # Runtime SQLite DB + logs (gitignored)
└── docs/                    # Screenshots
```

---

## Security

ORION includes multiple security layers:

- **API Key Authentication** — Set `ORION_API_KEY` in `.env` to require an `X-API-Key` header on all `/api/*` requests. When unset, auth is disabled (dev mode).
- **CSRF Protection** — All POST/PUT/DELETE requests must include `Content-Type: application/json`. Origin/Referer headers are validated when present.
- **Rate Limiting** — Per-IP sliding window: 10 req/min on scan triggers, 30 req/min on enrichment, 120 req/min on other API routes.
- **Security Headers** — CSP, X-Frame-Options (DENY), X-Content-Type-Options, X-XSS-Protection set on all responses.
- **CORS** — Restricted to `http://127.0.0.1:5000` by default. Configure via `CORS_ORIGINS` env var.
- **Input Validation** — MAC format regex, IP validation, integer bounds, JSON null checks on all endpoints.
- **No Secrets in Responses** — API errors return generic messages; details logged server-side only.
- **Thread Safety** — RLock on database, Lock on scanner state and alert manager, threading.Event for lifecycle.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/scan/current` | Current scan results (WiFi + BLE + Network) |
| POST | `/api/scan/trigger/wifi` | Trigger immediate WiFi scan |
| POST | `/api/scan/trigger/ble` | Trigger immediate BLE scan |
| POST | `/api/scan/trigger/network` | Trigger immediate network scan |
| GET | `/api/devices/` | List all devices (`?type=wifi\|ble\|network&limit=500`) |
| GET | `/api/devices/<mac>` | Get single device details |
| POST | `/api/devices/<mac>/notes` | Update device notes |
| GET | `/api/intel/events` | List intel events (`?unacked=true&limit=100`) |
| POST | `/api/intel/events/<id>/ack` | Acknowledge intel event |
| POST | `/api/intel/events/ack-all` | Acknowledge all intel events |
| GET | `/api/intel/debrief` | Generate debrief (`?window=5`) |
| GET | `/api/enrich/oui/<mac>` | OUI vendor lookup |
| GET | `/api/enrich/wigle/<bssid>` | WiGLE geolocation lookup |
| GET | `/api/enrich/cve/<vendor>` | NVD CVE lookup |
| POST | `/api/enrich/ssid` | SSID analysis (body: `{"ssid": "..."}`) |
| GET | `/api/settings/` | Get current settings |
| POST | `/api/settings/scan-intervals` | Update scan intervals |
| POST | `/api/settings/toggles` | Update feature toggles |
| GET | `/api/alerts/` | List alerts (`?unacked=true&limit=50`) |
| POST | `/api/alerts/<id>/ack` | Acknowledge alert |
| POST | `/api/alerts/ack-all` | Acknowledge all alerts |
| GET | `/api/alerts/rules` | List alert rules |

All POST endpoints require `Content-Type: application/json`. If `ORION_API_KEY` is set, include `X-API-Key: <your-key>` header.

---

## Configuration (.env)

```env
# App
ORION_HOST=127.0.0.1        # Bind address (0.0.0.0 for LAN access)
ORION_PORT=5000              # Server port
ORION_DEBUG=false            # Flask debug mode
ORION_LOG_LEVEL=INFO         # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Security
SECRET_KEY=                  # Flask session key (auto-generated if unset)
ORION_API_KEY=               # API key for /api/* routes (disabled if unset)
CORS_ORIGINS=http://127.0.0.1:5000  # Comma-separated allowed origins

# Feature toggles
ENABLE_WIFI=true             # Enable WiFi scanning
ENABLE_BLE=true              # Enable BLE scanning
ENABLE_NETWORK=true          # Enable network scanning
ENABLE_ENRICHMENT=false      # Enable enrichment API calls

# Scan intervals (seconds, range: 5-3600)
WIFI_SCAN_INTERVAL=30
BLE_SCAN_INTERVAL=20
NETWORK_SCAN_INTERVAL=120

# Risk thresholds
RISK_WARN_THRESHOLD=50
RISK_ALERT_THRESHOLD=75

# Enrichment API keys (all optional)
WIGLE_API_NAME=              # WiGLE.net API name
WIGLE_API_TOKEN=             # WiGLE.net API token
SHODAN_API_KEY=              # Shodan API key
MACADDRESS_IO_KEY=           # macaddress.io API key
```

---

## Enrichment Setup (Optional)

All enrichment APIs are optional. ORION runs fully offline without them.

### WiGLE (WiFi Geolocation)
1. Create account at https://wigle.net
2. Go to Account > API Token
3. Set `WIGLE_API_NAME` and `WIGLE_API_TOKEN` in `.env`

### Shodan (IP Intelligence)
1. Create account at https://account.shodan.io
2. Copy API key
3. Set `SHODAN_API_KEY` in `.env`

### NVD (CVE Lookup)
- No API key required for basic use (rate limited to 5 req/30s)

### macaddress.io (Vendor Details)
1. Register at https://macaddress.io
2. Get API key
3. Set `MACADDRESS_IO_KEY` in `.env`

---

## Updating the OUI Database

The bundled `static/data/oui.json` contains a minimal set of common vendors. To get the full IEEE OUI database:

1. Download from https://standards-oui.ieee.org/oui/oui.txt
2. Convert to JSON format with MAC prefix as key, vendor as value
3. Replace `static/data/oui.json`

---

## Testing

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

47 tests covering scanners, risk scoring, OUI lookup, device classification, and all API endpoints.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes
4. Run tests: `python -m pytest tests/ -v`
5. Submit a pull request

---

## Legal & Ethical Use

ORION is designed for **defensive security** and **personal privacy protection**. Intended use cases:

- Detecting hidden cameras in rental properties (Airbnb, hotels)
- Finding unauthorized tracking devices (AirTags)
- Auditing your own network for rogue devices
- Security research and education

**Do not** use ORION to:
- Monitor networks you don't own or have authorization to test
- Track individuals without consent
- Conduct unauthorized surveillance
- Violate local laws regarding wireless scanning

Users are solely responsible for ensuring compliance with applicable laws in their jurisdiction.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
