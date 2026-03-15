import json
import logging
import os

logger = logging.getLogger(__name__)


class BTUUIDLookup:
    """
    Bluetooth SIG UUID registry lookup.
    Uses bundled bt_uuids.json for offline lookup.
    """

    def __init__(self, bt_uuid_path: str):
        self.bt_uuid_path = bt_uuid_path
        self._db = {}
        self._db_clean = {}
        self._load()

    def _load(self):
        if os.path.exists(self.bt_uuid_path):
            try:
                with open(self.bt_uuid_path, 'r') as f:
                    self._db = json.load(f)
            except Exception as e:
                logger.warning("Failed to load BT UUID database from %s: %s", self.bt_uuid_path, e)
                self._db = {}

        # Build secondary index: cleaned keys (stripped 0x prefix, uppercase) -> value
        self._db_clean = {}
        for key, val in self._db.items():
            clean_key = key.upper().replace('0X', '').replace('-', '')[:8]
            self._db_clean[clean_key] = val

    def lookup(self, uuid: str) -> str:
        """Look up a Bluetooth UUID to get its service name."""
        if not uuid:
            return 'Unknown'

        # Try direct match
        uuid_upper = uuid.upper()
        if uuid_upper in self._db:
            return self._db[uuid_upper]

        # Try with 0x prefix
        if not uuid_upper.startswith('0X'):
            prefixed = f'0x{uuid_upper}'
            if prefixed in self._db:
                return self._db[prefixed]

        # Try short UUID using pre-built cleaned index
        short = uuid_upper.replace('-', '').replace('0X', '')[:8]
        if short in self._db_clean:
            return self._db_clean[short]

        return 'Unknown'

    def get_all(self) -> dict:
        return self._db.copy()


if __name__ == '__main__':
    lookup = BTUUIDLookup('')
    print("BT UUID lookup module loaded")
