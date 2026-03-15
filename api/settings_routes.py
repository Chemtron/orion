import logging

from flask import Blueprint, jsonify, request, current_app

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/', methods=['GET'])
def get_settings():
    try:
        config = current_app.config['ORION_CONFIG']
        return jsonify({
            'platform': config.platform,
            'host': config.host,
            'port': config.port,
            'debug': config.debug,
            'wifi_scan_interval': config.wifi_scan_interval,
            'ble_scan_interval': config.ble_scan_interval,
            'network_scan_interval': config.network_scan_interval,
            'enable_wifi_scan': config.enable_wifi_scan,
            'enable_ble_scan': config.enable_ble_scan,
            'enable_network_scan': config.enable_network_scan,
            'enable_enrichment': config.enable_enrichment,
            'enrichment_status': {
                'wigle': bool(config.wigle_api_name),
                'shodan': bool(config.shodan_api_key),
                'macaddress_io': bool(config.macaddress_io_key),
            }
        })
    except Exception as e:
        logger.exception("Error getting settings")
        return jsonify({'error': 'Internal server error'}), 500


def _validate_interval(value):
    """Validate and clamp a scan interval to bounds [5, 3600]."""
    try:
        val = int(value)
    except (ValueError, TypeError):
        return None, 'Invalid integer value'
    if val < 5 or val > 3600:
        return None, f'Scan interval must be between 5 and 3600 seconds, got {val}'
    return val, None


@settings_bp.route('/scan-intervals', methods=['POST'])
def update_scan_intervals():
    try:
        config = current_app.config['ORION_CONFIG']
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        for key in ('wifi_scan_interval', 'ble_scan_interval', 'network_scan_interval'):
            if key in data:
                val, err = _validate_interval(data[key])
                if err:
                    return jsonify({'error': f'{key}: {err}'}), 400
                setattr(config, key, val)
        logger.info("Scan intervals updated: %s", {k: data[k] for k in ('wifi_scan_interval', 'ble_scan_interval', 'network_scan_interval') if k in data})
        return jsonify({'status': 'updated'})
    except Exception as e:
        logger.exception("Error updating scan intervals")
        return jsonify({'error': 'Internal server error'}), 500


@settings_bp.route('/toggles', methods=['POST'])
def update_toggles():
    try:
        config = current_app.config['ORION_CONFIG']
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        if 'enable_wifi_scan' in data:
            config.enable_wifi_scan = bool(data['enable_wifi_scan'])
        if 'enable_ble_scan' in data:
            config.enable_ble_scan = bool(data['enable_ble_scan'])
        if 'enable_network_scan' in data:
            config.enable_network_scan = bool(data['enable_network_scan'])
        if 'enable_enrichment' in data:
            config.enable_enrichment = bool(data['enable_enrichment'])
        logger.info("Toggles updated: %s", {k: data[k] for k in ('enable_wifi_scan', 'enable_ble_scan', 'enable_network_scan', 'enable_enrichment') if k in data})
        return jsonify({'status': 'updated'})
    except Exception as e:
        logger.exception("Error updating toggles")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("settings_routes module loaded")
