import logging
import re
import requests
from typing import Optional, Dict

logger = logging.getLogger(__name__)

_MAC_RE = re.compile(r'^([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}$|^[0-9A-Fa-f]{12}$')


class MacAddressLookup:
    """
    macaddress.io vendor details lookup.
    API docs: https://macaddress.io/api
    """
    BASE_URL = 'https://api.macaddress.io/v1'

    def __init__(self, api_key: str):
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def lookup(self, mac: str) -> Optional[Dict]:
        if not self.is_configured():
            return None

        # Validate MAC format
        if not mac or not _MAC_RE.match(mac):
            logger.warning("Invalid MAC address format: %s", mac)
            return None

        try:
            resp = requests.get(
                self.BASE_URL,
                params={'apiKey': self.api_key, 'output': 'json', 'search': mac},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                vendor = data.get('vendorDetails', {})
                return {
                    'mac': mac,
                    'vendor': vendor.get('companyName', 'Unknown'),
                    'company_address': vendor.get('companyAddress', ''),
                    'country': vendor.get('countryCode', ''),
                    'is_private': data.get('macAddressDetails', {}).get('isPrivate', False),
                    'block_type': data.get('blockDetails', {}).get('blockType', ''),
                    'source': 'macaddress.io'
                }
            else:
                logger.warning("macaddress.io API returned status %d for MAC %s", resp.status_code, mac)
        except Exception as e:
            logger.warning("macaddress.io API error for MAC %s: %s", mac, e)
        return None


if __name__ == '__main__':
    m = MacAddressLookup('')
    print(f"Configured: {m.is_configured()}")
