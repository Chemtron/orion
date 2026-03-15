import os
import platform
from dotenv import load_dotenv

load_dotenv()

VALID_LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')


class Config:
    def _int_env(self, key, default):
        """Parse an integer from an environment variable, returning default on failure."""
        raw = os.getenv(key)
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:
            print(f"Warning: Invalid integer for {key}={raw!r}, using default {default}")
            return default

    def _get_secret(self, key):
        """Read a secret from the environment on demand."""
        return os.getenv(key, '')

    def __init__(self):
        # App
        self.host = os.getenv('ORION_HOST', '127.0.0.1')
        self.port = self._int_env('ORION_PORT', 5000)
        if not (1 <= self.port <= 65535):
            print(f"Warning: Port {self.port} out of range (1-65535), defaulting to 5000")
            self.port = 5000
        self.debug = os.getenv('ORION_DEBUG', 'false').lower() == 'true'
        self.log_level = os.getenv('ORION_LOG_LEVEL', 'INFO').upper()
        if self.log_level not in VALID_LOG_LEVELS:
            print(f"Warning: Invalid log level '{self.log_level}', defaulting to INFO")
            self.log_level = 'INFO'

        # Platform detection
        system = platform.system().lower()
        machine = platform.machine().lower()
        if 'android' in os.environ.get('PREFIX', '').lower() or os.path.exists('/data/data/com.termux'):
            self.platform = 'termux'
        elif system == 'linux' and ('arm' in machine or 'aarch' in machine):
            self.platform = 'raspberrypi'
        elif system == 'linux':
            self.platform = 'linux'
        elif system == 'windows':
            self.platform = 'windows'
        else:
            self.platform = 'unknown'

        # Paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.static_dir = os.path.join(self.base_dir, 'static')
        self.db_path = os.path.join(self.data_dir, 'orion.db')
        self.oui_path = os.path.join(self.static_dir, 'data', 'oui.json')
        self.bt_uuid_path = os.path.join(self.static_dir, 'data', 'bt_uuids.json')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'logs'), exist_ok=True)

        # Scan intervals (seconds)
        self.wifi_scan_interval = self._int_env('WIFI_SCAN_INTERVAL', 30)
        self.ble_scan_interval = self._int_env('BLE_SCAN_INTERVAL', 20)
        self.network_scan_interval = self._int_env('NETWORK_SCAN_INTERVAL', 120)

        # Risk scoring
        self.risk_score_threshold_warn = self._int_env('RISK_WARN_THRESHOLD', 50)
        self.risk_score_threshold_alert = self._int_env('RISK_ALERT_THRESHOLD', 75)

        # Feature flags
        self.enable_wifi_scan = os.getenv('ENABLE_WIFI', 'true').lower() == 'true'
        self.enable_ble_scan = os.getenv('ENABLE_BLE', 'true').lower() == 'true'
        self.enable_network_scan = os.getenv('ENABLE_NETWORK', 'true').lower() == 'true'
        self.enable_enrichment = os.getenv('ENABLE_ENRICHMENT', 'false').lower() == 'true'
        self.enable_wigle_contrib = os.getenv('ENABLE_WIGLE_CONTRIB', 'false').lower() == 'true'

    # Enrichment API keys as properties — read from env on demand
    @property
    def wigle_api_name(self):
        return self._get_secret('WIGLE_API_NAME')

    @property
    def wigle_api_token(self):
        return self._get_secret('WIGLE_API_TOKEN')

    @property
    def shodan_api_key(self):
        return self._get_secret('SHODAN_API_KEY')

    @property
    def macaddress_io_key(self):
        return self._get_secret('MACADDRESS_IO_KEY')

    @property
    def google_geo_api_key(self):
        return self._get_secret('GOOGLE_GEO_API_KEY')


if __name__ == '__main__':
    c = Config()
    print(f"Platform: {c.platform}")
    print(f"DB: {c.db_path}")
