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
