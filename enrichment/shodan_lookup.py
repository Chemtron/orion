import ipaddress
import logging
import requests
from typing import Optional, Dict

from core.cache import TTLCache

logger = logging.getLogger(__name__)


class ShodanLookup:
    """
    Shodan IP/device lookup.
    Requires API key from https://account.shodan.io
    """
    BASE_URL = 'https://api.shodan.io'
    _cache = TTLCache(default_ttl=1800)
    _NOT_FOUND = object()

    def __init__(self, api_key: str):
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def lookup_ip(self, ip: str) -> Optional[Dict]:
        if not self.is_configured():
            return None

        # Validate IP address format
        try:
            ipaddress.ip_address(ip)
        except ValueError as e:
            logger.warning("Invalid IP address '%s': %s", ip, e)
            return None

        cached = self._cache.get(f'shodan:{ip}')
        if cached is self._NOT_FOUND:
            return None
        if cached is not None:
            return cached

        try:
            resp = requests.get(
                f"{self.BASE_URL}/shodan/host/{ip}",
                # Shodan's API requires the key as a query parameter
                params={'key': self.api_key},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                result = {
                    'ip': ip,
                    'os': data.get('os'),
                    'ports': data.get('ports', []),
                    'hostnames': data.get('hostnames', []),
                    'org': data.get('org'),
                    'isp': data.get('isp'),
                    'country': data.get('country_name'),
                    'city': data.get('city'),
                    'vulns': data.get('vulns', []),
                    'source': 'shodan'
                }
                self._cache.set(f'shodan:{ip}', result)
                return result
            else:
                logger.warning("Shodan API returned status %d for IP %s", resp.status_code, ip)
        except Exception as e:
            logger.warning("Shodan API error for IP %s: %s", ip, e)
        self._cache.set(f'shodan:{ip}', self._NOT_FOUND, ttl=600)
        return None

    def search_device(self, query: str) -> list:
        if not self.is_configured():
            return []
        try:
            resp = requests.get(
                f"{self.BASE_URL}/shodan/host/search",
                # Shodan's API requires the key as a query parameter
                params={'key': self.api_key, 'query': query},
                timeout=15
            )
            if resp.status_code == 200:
                return resp.json().get('matches', [])
            else:
                logger.warning("Shodan API returned status %d for query '%s'", resp.status_code, query)
        except Exception as e:
            logger.warning("Shodan API error for query '%s': %s", query, e)
        return []


if __name__ == '__main__':
    s = ShodanLookup('')
    print(f"Configured: {s.is_configured()}")
