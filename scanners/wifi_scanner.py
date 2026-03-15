import subprocess
import json
import os
import math
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

FREQ_TO_CHANNEL = {
    2412: 1, 2417: 2, 2422: 3, 2427: 4, 2432: 5,
    2437: 6, 2442: 7, 2447: 8, 2452: 9, 2457: 10,
    2462: 11, 2467: 12, 2472: 13, 2484: 14,
}


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
            # Start the API service first
            subprocess.run(
                ['termux-api-start'],
                capture_output=True, timeout=5
            )
        except Exception:
            pass  # Continue even if this fails

        for attempt in range(2):
            try:
                result = subprocess.run(
                    ['termux-wifi-scaninfo'],
                    capture_output=True, text=True, timeout=25
                )
                if result.stdout.strip():
                    raw = json.loads(result.stdout)
                    return [self._normalize_termux(ap) for ap in raw]
                elif attempt == 0:
                    import time
                    time.sleep(3)
            except subprocess.TimeoutExpired:
                logger.warning("WiFi Termux scan timed out (attempt %d)", attempt + 1)
                if attempt == 0:
                    import time
                    time.sleep(3)
                    continue
                return []
            except Exception as e:
                logger.warning("WiFi Termux scan error: %s", e)
                return []
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
        except Exception as e:
            logger.warning("WiFi iwlist scan error: %s", e)
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
        except Exception as e:
            logger.warning("WiFi Windows scan error: %s", e)
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
                ['iwconfig'], capture_output=True, text=True, timeout=10
            )
            interfaces = []
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line:
                    interfaces.append(line.split()[0])
            return interfaces
        except Exception as e:
            logger.warning("WiFi interface detection error: %s", e)
            return ['wlan0']

    def _freq_to_channel(self, freq_mhz: int) -> int:
        channel = FREQ_TO_CHANNEL.get(freq_mhz)
        if channel is not None:
            return channel
        if 5000 <= freq_mhz <= 5900:
            return (freq_mhz - 5000) // 5
        return 0

    def _estimate_distance(self, rssi: int, tx_power: int = -59, n: float = 2.5) -> float:
        if rssi == 0:
            return -1.0
        try:
            return round(10 ** ((tx_power - rssi) / (10 * n)), 1)
        except Exception as e:
            logger.warning("WiFi distance estimation error: %s", e)
            return -1.0

    def _parse_nmcli_line(self, line: str) -> dict:
        try:
            safe = line.replace('\\:', '\x00')
            parts = safe.split(':')
            bssid_parts = parts[:6]
            bssid = ':'.join(p.replace('\x00', ':') for p in bssid_parts).upper()
            remaining = parts[6:]
            if len(remaining) >= 4:
                ssid = remaining[0].replace('\x00', ':')
                freq_str = remaining[1].replace('\x00', ':')
                signal = int(remaining[2]) if remaining[2].strip().isdigit() else -70
                security = remaining[3].replace('\x00', ':').strip()
                freq_mhz = int(''.join(filter(str.isdigit, freq_str[:5]))) if freq_str else 2412
                rssi = (signal * 2) - 100
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
        except Exception as e:
            logger.warning("WiFi nmcli parse error: %s", e)
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
                    if rssi > 0:
                        rssi = rssi - 100
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
        for d in devices:
            d.setdefault('frequency_mhz', 2412)
            d.setdefault('channel', 6)
            d.setdefault('band', '2.4GHz')
            d.setdefault('hidden', False)
            d.setdefault('source', 'netsh')
        return devices


if __name__ == '__main__':
    from core.config import Config
    config = Config()
    scanner = WiFiScanner(config)
    results = scanner.scan()
    print(f"Found {len(results)} WiFi networks")
    for r in results[:5]:
        print(f"  {r.get('ssid', 'Hidden')} ({r.get('mac', '?')}) {r.get('rssi', '?')}dBm")
