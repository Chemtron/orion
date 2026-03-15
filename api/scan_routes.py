import logging
import threading

from flask import Blueprint, jsonify, current_app

logger = logging.getLogger(__name__)

scan_bp = Blueprint('scan', __name__)


@scan_bp.route('/current', methods=['GET'])
def get_current_scan():
    try:
        scanner = current_app.config['SCANNER']
        return jsonify(scanner.get_current_state())
    except Exception as e:
        logger.exception("Error getting current scan state")
        return jsonify({'error': 'Internal server error'}), 500


@scan_bp.route('/trigger/wifi', methods=['POST'])
def trigger_wifi():
    try:
        scanner = current_app.config['SCANNER']
        threading.Thread(target=scanner.run_wifi_scan, daemon=True).start()
        logger.info("WiFi scan triggered")
        return jsonify({'status': 'triggered', 'type': 'wifi'})
    except Exception as e:
        logger.exception("Error triggering WiFi scan")
        return jsonify({'error': 'Internal server error'}), 500


@scan_bp.route('/trigger/ble', methods=['POST'])
def trigger_ble():
    try:
        scanner = current_app.config['SCANNER']
        threading.Thread(target=scanner.run_ble_scan, daemon=True).start()
        logger.info("BLE scan triggered")
        return jsonify({'status': 'triggered', 'type': 'ble'})
    except Exception as e:
        logger.exception("Error triggering BLE scan")
        return jsonify({'error': 'Internal server error'}), 500


@scan_bp.route('/trigger/network', methods=['POST'])
def trigger_network():
    try:
        scanner = current_app.config['SCANNER']
        threading.Thread(target=scanner.run_network_scan, daemon=True).start()
        logger.info("Network scan triggered")
        return jsonify({'status': 'triggered', 'type': 'network'})
    except Exception as e:
        logger.exception("Error triggering network scan")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("scan_routes module loaded")
