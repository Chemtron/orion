import json
import logging
import os
from functools import lru_cache

logger = logging.getLogger(__name__)


class OUILookup:
    """
    Local IEEE OUI database lookup.
    Bundled oui.json at static/data/oui.json
    No internet required.
    """

    # NOTE: Keep in sync with analysis.risk_scorer.KNOWN_CAMERA_OUIS
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
        self._db_clean = {}
        self._load()

    def _load(self):
        if os.path.exists(self.oui_path):
            try:
                with open(self.oui_path, 'r') as f:
                    self._db = json.load(f)
            except Exception as e:
                logger.warning("Failed to load OUI database from %s: %s", self.oui_path, e)
                self._db = {}

        # Build secondary index: cleaned keys (no colons, uppercase, first 6 chars) -> value
        self._db_clean = {}
        for key, val in self._db.items():
            clean_key = key.replace(':', '').upper()[:6]
            self._db_clean[clean_key] = val

    @lru_cache(maxsize=4096)
    def lookup(self, mac: str) -> str:
        if not mac:
            return 'Unknown'
        oui = mac.upper()[:8]

        if oui in self.KNOWN_CAMERA_OUIS:
            return self.KNOWN_CAMERA_OUIS[oui]

        if oui in self._db:
            return self._db[oui]

        # Fallback: use pre-built cleaned index instead of O(n) scan
        oui_clean = oui.replace(':', '').upper()[:6]
        if oui_clean in self._db_clean:
            return self._db_clean[oui_clean]

        return 'Unknown'

    def is_camera_vendor(self, mac: str) -> bool:
        return mac.upper()[:8] in self.KNOWN_CAMERA_OUIS

    def is_espressif(self, mac: str) -> bool:
        espressif_ouis = {'24:0A:C4', '30:AE:A4', '24:6F:28', '3C:61:05',
                          'B8:D6:1A', 'CC:50:E3', 'A4:CF:12', '4C:EB:D6'}
        return mac.upper()[:8] in espressif_ouis


if __name__ == '__main__':
    lookup = OUILookup('')
    print(lookup.lookup('24:0A:C4:11:22:33'))
    print(lookup.is_camera_vendor('D4:5D:64:AA:BB:CC'))
