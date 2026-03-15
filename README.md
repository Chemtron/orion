# ORION — Open Source Passive Signal Intelligence Platform

**WiFi + BLE + Network scanning | OSINT enrichment | Tactical HUD**

ORION is a passive signal intelligence tool that scans for WiFi networks, Bluetooth Low Energy (BLE) devices, and LAN hosts. It scores devices for risk, detects potential surveillance hardware (hidden cameras, AirTags, rogue APs), and presents everything through a tactical radar HUD in your browser.

Built for **Android (Termux)**, **Raspberry Pi**, and **Linux**. Windows supported for development.

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
git clone https://github.com/YOUR_USERNAME/orion.git ~/orion
cd ~/orion
bash install.sh
python orion.py
# Open Chrome: http://127.0.0.1:5000
```

### Raspberry Pi / Linux
```bash
git clone https://github.com/YOUR_USERNAME/orion.git ~/orion
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

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/scan/current` | Current scan results (WiFi + BLE + Network) |
| POST | `/api/scan/trigger/wifi` | Trigger immediate WiFi scan |
| POST | `/api/scan/trigger/ble` | Trigger immediate BLE scan |
| POST | `/api/scan/trigger/network` | Trigger immediate network scan |
| GET | `/api/devices/` | List all devices (filter: `?type=wifi\|ble\|network`) |
| GET | `/api/devices/<mac>` | Get single device details |
| POST | `/api/devices/<mac>/notes` | Update device notes |
| GET | `/api/intel/events` | List intel events (filter: `?unacked=true`) |
| POST | `/api/intel/events/<id>/ack` | Acknowledge intel event |
| GET | `/api/intel/debrief` | Generate debrief (`?window=5`) |
| GET | `/api/enrich/oui/<mac>` | OUI vendor lookup |
| GET | `/api/enrich/wigle/<bssid>` | WiGLE geolocation lookup |
| GET | `/api/enrich/cve/<vendor>` | NVD CVE lookup |
| POST | `/api/enrich/ssid` | SSID analysis (body: `{"ssid": "..."}`) |
| GET | `/api/settings/` | Get current settings |
| POST | `/api/settings/scan-intervals` | Update scan intervals |
| POST | `/api/settings/toggles` | Update feature toggles |
| GET | `/api/alerts/` | List alerts |
| POST | `/api/alerts/<id>/ack` | Acknowledge alert |
| POST | `/api/alerts/ack-all` | Acknowledge all alerts |

---

## Configuration (.env)

```env
# App
ORION_HOST=127.0.0.1        # Bind address (0.0.0.0 for LAN access)
ORION_PORT=5000              # Server port
ORION_DEBUG=false            # Flask debug mode
ORION_LOG_LEVEL=INFO         # Logging level

# Feature toggles
ENABLE_WIFI=true             # Enable WiFi scanning
ENABLE_BLE=true              # Enable BLE scanning
ENABLE_NETWORK=true          # Enable network scanning
ENABLE_ENRICHMENT=false      # Enable enrichment API calls

# Scan intervals (seconds)
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

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes
4. Run tests: `pytest tests/ -v`
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
