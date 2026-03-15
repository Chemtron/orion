import json
import logging
from typing import Dict, Optional

from enrichment.oui_lookup import OUILookup
from enrichment.wigle_lookup import WiGLELookup
from enrichment.shodan_lookup import ShodanLookup
from enrichment.macaddress_lookup import MacAddressLookup
from enrichment.nvd_lookup import NVDLookup
from enrichment.bt_uuid_lookup import BTUUIDLookup

logger = logging.getLogger(__name__)


class EnrichmentManager:
    """
    Orchestrates all enrichment sources for a given device.
    Only calls APIs that are configured.
    """

    def __init__(self, config, db):
        self.config = config
        self.db = db

        self.oui = OUILookup(config.oui_path)
        self.wigle = WiGLELookup(config.wigle_api_name, config.wigle_api_token)
        self.shodan = ShodanLookup(config.shodan_api_key)
        self.macaddress = MacAddressLookup(config.macaddress_io_key)
        self.nvd = NVDLookup()
        self.bt_uuid = BTUUIDLookup(config.bt_uuid_path)

    def enrich_device(self, mac: str, device_type: str) -> Dict:
        """Run all configured enrichment sources on a device."""
        results = {}

        # OUI lookup (always available, local)
        results['vendor'] = self.oui.lookup(mac)
        results['is_camera_vendor'] = self.oui.is_camera_vendor(mac)

        # WiGLE geolocation
        if self.wigle.is_configured() and device_type == 'wifi':
            wigle_data = self.wigle.lookup_bssid(mac)
            if wigle_data:
                results['wigle'] = wigle_data

        # macaddress.io
        if self.macaddress.is_configured():
            mac_data = self.macaddress.lookup(mac)
            if mac_data:
                results['macaddress'] = mac_data

        # NVD CVE lookup based on vendor
        vendor = results.get('vendor', '')
        if vendor and vendor != 'Unknown':
            cves = self.nvd.lookup_vendor(vendor)
            if cves:
                results['cves'] = cves

        # Store enrichment data
        with self.db.get_conn() as conn:
            conn.execute(
                "UPDATE devices SET enriched=1, enrichment_data=? WHERE mac=? AND device_type=?",
                (json.dumps(results), mac, device_type)
            )

        return results

    def get_enrichment_status(self) -> Dict:
        """Return which enrichment services are available."""
        return {
            'oui': True,
            'wigle': self.wigle.is_configured(),
            'shodan': self.shodan.is_configured(),
            'macaddress': self.macaddress.is_configured(),
            'nvd': True,
            'bt_uuid': True
        }


if __name__ == '__main__':
    print("EnrichmentManager module loaded")
