#!/bin/bash
# ORION Installer — Termux (Android) / Raspberry Pi / Linux
set -e

ORION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================"
echo " ORION Signal Intelligence"
echo " Installer v1.0.1"
echo "================================"

# Detect platform
if [ -d "/data/data/com.termux" ] || echo "$PREFIX" | grep -q "com.termux"; then
  PLATFORM="termux"
elif [ -f /proc/device-tree/model ] && grep -q -i "raspberry" /proc/device-tree/model 2>/dev/null; then
  PLATFORM="raspberrypi"
else
  PLATFORM="linux"
fi

echo "[Platform] Detected: $PLATFORM"
echo ""

# ── TERMUX ──────────────────────────────────────────────
if [ "$PLATFORM" == "termux" ]; then

  echo "[+] Updating Termux packages..."
  pkg update -y && pkg upgrade -y

  echo "[+] Installing system packages..."
  pkg install -y python git nmap termux-api python-psutil

  echo "[+] Setting up storage access..."
  termux-setup-storage || true

  echo ""
  echo "⚠ REQUIRED: Make sure you have installed these TWO apps from F-Droid:"
  echo "   1. Termux         (terminal)"
  echo "   2. Termux:API     (hardware access — SEPARATE app)"
  echo ""
  echo "⚠ REQUIRED: Grant these permissions to Termux:API in Android Settings:"
  echo "   → Location: Allow all the time"
  echo "   → Nearby devices: Allow"
  echo ""
  read -p "Press Enter when both apps are installed and permissions are granted..."

  echo "[+] Installing Python packages..."
  pip install -r "$ORION_DIR/requirements-termux.txt"

  echo "[+] Testing Termux:API WiFi access..."
  termux-api-start 2>/dev/null || true
  sleep 2
  WIFI_TEST=$(termux-wifi-scaninfo 2>/dev/null | head -c 20)
  if [ -z "$WIFI_TEST" ]; then
    echo ""
    echo "⚠ WARNING: termux-wifi-scaninfo returned nothing."
    echo "  This usually means one of:"
    echo "  1. Termux:API app not installed from F-Droid"
    echo "  2. Location permission not granted to Termux:API"
    echo "  3. WiFi is turned off on the phone"
    echo "  The app will still run but WiFi scan will return empty."
    echo ""
  else
    echo "[✓] WiFi scan working"
  fi

  echo "[+] Testing BLE access..."
  termux-api-start 2>/dev/null || true

  echo ""
  echo "================================"
  echo " Installation complete!"
  echo " Run:  cd ~/orion && python orion.py"
  echo " Then open Chrome: http://127.0.0.1:5000"
  echo "================================"

# ── RASPBERRY PI ────────────────────────────────────────
elif [ "$PLATFORM" == "raspberrypi" ]; then

  echo "[+] Installing system packages..."
  sudo apt-get update -y
  sudo apt-get install -y python3 python3-pip nmap bluetooth bluez git \
    python3-psutil python3-netifaces

  echo "[+] Installing Python packages..."
  pip3 install -r "$ORION_DIR/requirements.txt" --break-system-packages 2>/dev/null || \
  pip3 install -r "$ORION_DIR/requirements.txt"

  echo "[+] Enabling Bluetooth service..."
  sudo systemctl enable bluetooth
  sudo systemctl start bluetooth

  echo ""
  echo "================================"
  echo " Installation complete!"
  echo " Run:  cd ~/orion && python3 orion.py"
  echo " Open from any LAN device:"
  echo " http://$(hostname -I | awk '{print $1}'):5000"
  echo "================================"

# ── LINUX ───────────────────────────────────────────────
else

  echo "[+] Installing system packages..."
  sudo apt-get update -y
  sudo apt-get install -y python3 python3-pip nmap bluetooth bluez git \
    python3-psutil python3-netifaces

  echo "[+] Installing Python packages..."
  pip3 install -r "$ORION_DIR/requirements.txt" --break-system-packages 2>/dev/null || \
  pip3 install -r "$ORION_DIR/requirements.txt"

  echo ""
  echo "================================"
  echo " Installation complete!"
  echo " Run:  cd ~/orion && python3 orion.py"
  echo " Open: http://127.0.0.1:5000"
  echo "================================"

fi

# Create data dirs
mkdir -p "$ORION_DIR/data/logs"

# Create .env if missing
if [ ! -f "$ORION_DIR/.env" ]; then
  cat > "$ORION_DIR/.env" << 'EOF'
ORION_HOST=127.0.0.1
ORION_PORT=5000
ORION_DEBUG=false
ENABLE_WIFI=true
ENABLE_BLE=true
ENABLE_NETWORK=true
ENABLE_ENRICHMENT=false
WIGLE_API_NAME=
WIGLE_API_TOKEN=
SHODAN_API_KEY=
MACADDRESS_IO_KEY=
EOF
  echo "[+] Created default .env"
fi
