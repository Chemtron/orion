import logging
import re

from flask import Blueprint, jsonify, request, current_app
from enrichment.oui_lookup import OUILookup
from enrichment.wigle_lookup import WiGLELookup
from enrichment.nvd_lookup import NVDLookup
from analysis.ssid_analyzer import SSIDAnalyzer

logger = logging.getLogger(__name__)

enrichment_bp = Blueprint('enrichment', __name__)


_MAC_RE = re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')


def _is_valid_mac(mac):
    """MAC address format validation."""
    return bool(_MAC_RE.match(mac))


@enrichment_bp.route('/oui/<mac>', methods=['GET'])
def lookup_oui(mac):
    try:
        if not _is_valid_mac(mac):
            return jsonify({'error': 'Invalid MAC address format (expected XX:XX:XX:XX:XX:XX)'}), 400
        config = current_app.config['ORION_CONFIG']
        if 'OUI_LOOKUP' not in current_app.config:
            current_app.config['OUI_LOOKUP'] = OUILookup(config.oui_path)
        oui = current_app.config['OUI_LOOKUP']
        return jsonify({
            'mac': mac,
            'vendor': oui.lookup(mac),
            'is_camera': oui.is_camera_vendor(mac),
            'is_espressif': oui.is_espressif(mac)
        })
    except Exception as e:
        logger.exception("Error looking up OUI for %s", mac)
        return jsonify({'error': 'Internal server error'}), 500


@enrichment_bp.route('/wigle/<bssid>', methods=['GET'])
def lookup_wigle(bssid):
    try:
        if not _is_valid_mac(bssid):
            return jsonify({'error': 'Invalid BSSID format (expected XX:XX:XX:XX:XX:XX)'}), 400
        config = current_app.config['ORION_CONFIG']
        if not config.wigle_api_name:
            return jsonify({'error': 'WiGLE not configured'}), 400
        wigle = WiGLELookup(config.wigle_api_name, config.wigle_api_token)
        result = wigle.lookup_bssid(bssid)
        return jsonify(result or {'error': 'Not found'})
    except Exception as e:
        logger.exception("Error looking up WiGLE for %s", bssid)
        return jsonify({'error': 'Internal server error'}), 500


@enrichment_bp.route('/cve/<vendor>', methods=['GET'])
def lookup_cve(vendor):
    try:
        nvd = NVDLookup()
        cves = nvd.lookup_vendor(vendor)
        return jsonify({'vendor': vendor, 'cves': cves, 'count': len(cves)})
    except Exception as e:
        logger.exception("Error looking up CVEs for %s", vendor)
        return jsonify({'error': 'Internal server error'}), 500


@enrichment_bp.route('/ssid', methods=['POST'])
def analyze_ssid():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        ssid = data.get('ssid', '')
        analyzer = SSIDAnalyzer()
        return jsonify(analyzer.analyze(ssid))
    except Exception as e:
        logger.exception("Error analyzing SSID")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("enrichment_routes module loaded")
