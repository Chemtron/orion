import logging

from flask import Blueprint, jsonify, request, current_app

logger = logging.getLogger(__name__)

device_bp = Blueprint('devices', __name__)


@device_bp.route('/', methods=['GET'])
def get_devices():
    try:
        db = current_app.config['DB']
        device_type = request.args.get('type')
        try:
            limit = int(request.args.get('limit', 500))
        except ValueError:
            limit = 500
        devices = db.get_all_devices(device_type=device_type, limit=limit)
        return jsonify({'devices': devices, 'count': len(devices)})
    except Exception as e:
        logger.exception("Error getting devices")
        return jsonify({'error': 'Internal server error'}), 500


@device_bp.route('/<mac>', methods=['GET'])
def get_device(mac):
    try:
        db = current_app.config['DB']
        device_type = request.args.get('type', 'wifi')
        device = db.get_device(mac, device_type)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        return jsonify(device)
    except Exception as e:
        logger.exception("Error getting device %s", mac)
        return jsonify({'error': 'Internal server error'}), 500


@device_bp.route('/<mac>/notes', methods=['POST'])
def update_notes(mac):
    try:
        db = current_app.config['DB']
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        device_type = data.get('type', 'wifi')
        notes = data.get('notes', '')
        with db.get_conn() as conn:
            conn.execute(
                "UPDATE devices SET notes=? WHERE mac=? AND device_type=?",
                (notes, mac, device_type)
            )
        logger.info("Updated notes for device %s", mac)
        return jsonify({'status': 'updated'})
    except Exception as e:
        logger.exception("Error updating notes for device %s", mac)
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("device_routes module loaded")
