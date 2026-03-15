import logging

logger = logging.getLogger(__name__)

# Canonical list of known camera/IoT vendor OUI prefixes.
# Other modules should reference this set as the authoritative source.
KNOWN_CAMERA_OUIS = {
    '24:0A:C4', '30:AE:A4', '24:6F:28', '3C:61:05',
    'D4:5D:64', 'B4:A2:EB', 'BC:32:5F',
    'E0:0A:F6', '8C:E7:48', 'AC:CF:85',
    'DC:44:27', 'C8:02:8F',
    'E4:AB:89',
}


class RiskScorer:
    """
    Scores WiFi, BLE, and network devices on a 0-100 risk scale.
    Returns score + list of flag strings.
    """

    KNOWN_CAMERA_OUIS = KNOWN_CAMERA_OUIS

    SUSPICIOUS_SSID_PATTERNS = [
        'cam', 'camera', 'spy', 'hidden', 'reolink', 'hikvision',
        'dahua', 'wyze', 'ring', 'nest', 'arlo', 'blink',
        'ip-cam', 'ipcam', 'nvr', 'dvr', 'cctv'
    ]

    DEFAULT_ROUTER_PATTERNS = [
        'netgear', 'linksys', 'tp-link', 'tplink', 'fritz',
        'xfinity', 'spectrum', 'att-', 'default', 'dlink'
    ]

    def __init__(self, config=None):
        self.config = config

    def score_wifi(self, device: dict) -> dict:
        score = 0
        flags = []
        ssid = (device.get('ssid') or '').lower()
        security = (device.get('security') or '').upper()
        mac = (device.get('mac') or '').upper()
        rssi = device.get('rssi', -80)
        hidden = device.get('hidden', False)

        if 'WPA' not in security and 'WEP' not in security:
            score += 30
            flags.append('OPEN_NETWORK')

        if hidden:
            score += 20
            flags.append('HIDDEN_SSID')

        if any(p in ssid for p in self.SUSPICIOUS_SSID_PATTERNS):
            score += 25
            flags.append('CAMERA_SSID_KEYWORD')

        oui = mac[:8]
        if oui in self.KNOWN_CAMERA_OUIS:
            score += 35
            flags.append('CAMERA_VENDOR_OUI')

        if any(p in ssid for p in self.DEFAULT_ROUTER_PATTERNS):
            score += 10
            flags.append('DEFAULT_ROUTER_SSID')

        if rssi > -40:
            score += 10
            flags.append('VERY_STRONG_SIGNAL')

        if 'WEP' in security:
            score += 15
            flags.append('WEAK_ENCRYPTION_WEP')

        return {'score': min(score, 100), 'flags': flags}

    def score_ble(self, device: dict) -> dict:
        score = 0
        flags = []
        is_airtag = device.get('is_airtag', False)
        hints = device.get('device_hints', [])
        name = (device.get('name') or '').lower()
        mac = (device.get('mac') or '').upper()
        rssi = device.get('rssi', -80)

        if is_airtag:
            score += 70
            flags.append('AIRTAG_DETECTED')
        elif 'AIRTAG_CANDIDATE' in hints:
            score += 50
            flags.append('AIRTAG_CANDIDATE')

        oui = mac[:8]
        if oui in self.KNOWN_CAMERA_OUIS:
            score += 40
            flags.append('CAMERA_VENDOR_OUI')

        is_apple = device.get('is_apple', False)
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


if __name__ == '__main__':
    scorer = RiskScorer()
    result = scorer.score_wifi({'ssid': 'HiddenCam', 'security': 'OPEN', 'mac': '24:0A:C4:11:22:33'})
    print(f"Score: {result['score']}, Flags: {result['flags']}")
