import logging
import threading

logger = logging.getLogger(__name__)


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
        self._max_fired = 10000
        self._lock = threading.Lock()

    def evaluate_wifi(self, device: dict):
        self._evaluate(device, 'wifi')

    def evaluate_ble(self, device: dict):
        self._evaluate(device, 'ble')

    def _evaluate(self, device: dict, scan_type: str):
        mac = device.get('mac', '')

        with self._lock:
            if len(self._fired) > self._max_fired:
                self._fired.clear()

            for rule in self.RULES:
                try:
                    if rule['check'](device):
                        key = f"{rule['name']}_{mac}"
                        if key not in self._fired:
                            self._fired.add(key)
                            logger.info("Alert fired: [%s] %s for device %s", rule['severity'], rule['title'], mac)
                            self.db.log_intel_event(
                                event_type=rule['type'],
                                severity=rule['severity'],
                                title=rule['title'],
                                device_mac=mac,
                                ssid=device.get('ssid'),
                                detail=f"Flags: {device.get('risk_flags')} | Score: {device.get('risk_score')}"
                            )
                except Exception as e:
                    logger.warning("Error evaluating rule '%s' for device %s: %s", rule['name'], mac, e)
                    continue

    def get_rules(self) -> list:
        return [{'name': r['name'], 'severity': r['severity'], 'title': r['title']} for r in self.RULES]


if __name__ == '__main__':
    print("AlertManager module loaded")
