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


@scan_bp.route('/diagnostics', methods=['GET'])
def diagnostics():
    import subprocess as _sp
    try:
        config = current_app.config['ORION_CONFIG']

        results = {
            'platform': config.platform,
            'checks': {}
        }

        # Check termux-wifi-scaninfo
        try:
            _sp.run(['termux-wifi-scaninfo'], capture_output=True, timeout=3)
            results['checks']['termux_wifi'] = 'available'
        except FileNotFoundError:
            results['checks']['termux_wifi'] = 'not_found'
        except _sp.TimeoutExpired:
            results['checks']['termux_wifi'] = 'timeout'
        except Exception as e:
            results['checks']['termux_wifi'] = str(e)

        # Check termux-api-start
        try:
            _sp.run(['termux-api-start'], capture_output=True, timeout=3)
            results['checks']['termux_api'] = 'available'
        except FileNotFoundError:
            results['checks']['termux_api'] = 'not_found'
        except Exception as e:
            results['checks']['termux_api'] = str(e)

        # Check nmap
        try:
            _sp.run(['nmap', '--version'], capture_output=True, timeout=5)
            results['checks']['nmap'] = 'available'
        except FileNotFoundError:
            results['checks']['nmap'] = 'not_found'
        except Exception as e:
            results['checks']['nmap'] = str(e)

        # Check bleak
        try:
            import bleak
            results['checks']['bleak'] = 'available'
        except ImportError:
            results['checks']['bleak'] = 'not_installed'

        # Check bluetoothctl
        try:
            _sp.run(['bluetoothctl', '--version'], capture_output=True, timeout=3)
            results['checks']['bluetoothctl'] = 'available'
        except FileNotFoundError:
            results['checks']['bluetoothctl'] = 'not_found'
        except Exception as e:
            results['checks']['bluetoothctl'] = str(e)

        return jsonify(results)
    except Exception as e:
        logger.exception("Error running diagnostics")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("scan_routes module loaded")
