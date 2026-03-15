import subprocess
import json
import asyncio
import threading
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


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

    AIRTAG_PAYLOAD_MARKER = bytes([0x12, 0x19])

    def __init__(self, config):
        self.config = config
        self.platform = config.platform

    def scan(self) -> List[Dict]:
        if self.platform == 'termux':
            return self._scan_termux()
        elif self.platform in ('linux', 'raspberrypi'):
            return self._scan_linux()
        elif self.platform == 'windows':
            return self._scan_windows_bleak()
        else:
            return self._scan_mock_ble()

    def _scan_termux(self) -> List[Dict]:
        # Try bleak first (works on some Android/Termux setups)
        try:
            import bleak
            import asyncio
            loop = asyncio.new_event_loop()
            devices = loop.run_until_complete(self._bleak_scan(timeout=5.0))
            loop.close()
            if devices:
                return devices
        except Exception as e:
            logger.info("BLE bleak not available on Termux: %s", e)

        # BLE not available on this Termux setup - return empty gracefully
        # User will see 0 BLE devices which is correct behavior
        logger.info("BLE scanning not available on Termux — returning empty")
        return []

    def _scan_linux(self) -> List[Dict]:
        try:
            import bleak
            devices = asyncio.run(self._bleak_scan())
            return devices
        except ImportError:
            return self._bluetoothctl_scan()
        except Exception as e:
            logger.warning("BLE Linux bleak scan error: %s", e)
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
        try:
            import bleak
            devices = asyncio.run(self._bleak_scan(timeout=4.0))
            return devices
        except Exception as e:
            logger.warning("BLE Windows bleak scan error: %s", e)
            return self._scan_mock_ble()

    def _bluetoothctl_scan(self) -> List[Dict]:
        proc = None
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
        except FileNotFoundError:
            logger.warning("bluetoothctl not found — BLE scanning unavailable on this platform")
            return []
        except Exception as e:
            logger.warning("BLE bluetoothctl scan error: %s", e)
            if proc is not None:
                try:
                    proc.kill()
                    proc.wait()
                except OSError:
                    pass
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
                        'rssi': -70,
                        'distance_m': -1,
                        'manufacturer_data': {},
                        'service_uuids': [],
                        'device_hints': [],
                        'is_apple': False,
                        'is_airtag': False,
                        'source': 'bluetoothctl'
                    })
                except Exception as e:
                    logger.warning("BLE bluetoothctl parse error: %s", e)
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
        except Exception as e:
            logger.warning("BLE distance estimation error: %s", e)
            return -1.0

    def _scan_mock_ble(self) -> List[Dict]:
        import random
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


if __name__ == '__main__':
    from core.config import Config
    config = Config()
    scanner = BLEScanner(config)
    results = scanner.scan()
    print(f"Found {len(results)} BLE devices")
    for r in results[:5]:
        print(f"  {r.get('name', 'Unknown')} ({r.get('mac', '?')}) {r.get('rssi', '?')}dBm")
