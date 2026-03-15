import logging
import requests
import base64
from typing import Optional, Dict

from core.cache import TTLCache

logger = logging.getLogger(__name__)


class WiGLELookup:
    """
    WiGLE.net BSSID geolocation lookup.
    Free account: ~10 queries/day
    API docs: https://api.wigle.net/swagger
    """
    BASE_URL = 'https://api.wigle.net/api/v2'
    _cache = TTLCache(default_ttl=3600)
    _NOT_FOUND = object()

    def __init__(self, api_name: str, api_token: str):
        self.api_name = api_name
        self.api_token = api_token
        self._auth = base64.b64encode(
            f"{api_name}:{api_token}".encode()
        ).decode() if api_name and api_token else None

    def is_configured(self) -> bool:
        return bool(self._auth)

    def lookup_bssid(self, bssid: str) -> Optional[Dict]:
        if not self.is_configured():
            logger.warning("WiGLE lookup not configured — missing API credentials")
            return None

        cached = self._cache.get(f'wigle:{bssid}')
        if cached is self._NOT_FOUND:
            return None
        if cached is not None:
            return cached

        try:
            resp = requests.get(
                f"{self.BASE_URL}/network/search",
                params={'netid': bssid},
                headers={'Authorization': f'Basic {self._auth}'},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get('results', [])
                if results:
                    r = results[0]
                    result = {
                        'bssid': bssid,
                        'ssid': r.get('ssid'),
                        'latitude': r.get('trilat'),
                        'longitude': r.get('trilong'),
                        'first_seen': r.get('firsttime'),
                        'last_seen': r.get('lasttime'),
                        'country': r.get('country'),
                        'city': r.get('city'),
                        'source': 'wigle'
                    }
                    self._cache.set(f'wigle:{bssid}', result)
                    return result
            else:
                logger.warning("WiGLE API returned status %d for BSSID %s", resp.status_code, bssid)
        except Exception as e:
            logger.warning("WiGLE API error for BSSID %s: %s", bssid, e)
        self._cache.set(f'wigle:{bssid}', self._NOT_FOUND, ttl=600)
        return None

    def search_ssid(self, ssid: str, lat: float = None, lon: float = None) -> list:
        if not self.is_configured():
            logger.warning("WiGLE lookup not configured — missing API credentials")
            return []
        params = {'ssid': ssid, 'freenet': 'false', 'paynet': 'false'}
        if lat and lon:
            params.update({'latrange1': lat - 0.1, 'latrange2': lat + 0.1,
                           'longrange1': lon - 0.1, 'longrange2': lon + 0.1})
        try:
            resp = requests.get(
                f"{self.BASE_URL}/network/search",
                params=params,
                headers={'Authorization': f'Basic {self._auth}'},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json().get('results', [])
            else:
                logger.warning("WiGLE API returned status %d for SSID %s", resp.status_code, ssid)
        except Exception as e:
            logger.warning("WiGLE API error for SSID %s: %s", ssid, e)
        return []


if __name__ == '__main__':
    w = WiGLELookup('', '')
    print(f"Configured: {w.is_configured()}")
