import logging

from flask import Blueprint, jsonify, request, current_app
from intel.alert_manager import AlertManager

logger = logging.getLogger(__name__)

alert_bp = Blueprint('alerts', __name__)


@alert_bp.route('/', methods=['GET'])
def get_alerts():
    try:
        db = current_app.config['DB']
        try:
            limit = int(request.args.get('limit', 50))
        except ValueError:
            limit = 50
        unacked = request.args.get('unacked', 'false').lower() == 'true'
        events = db.get_intel_events(limit=limit, unacked_only=unacked)
        return jsonify({'alerts': events, 'count': len(events)})
    except Exception as e:
        logger.exception("Error getting alerts")
        return jsonify({'error': 'Internal server error'}), 500


@alert_bp.route('/<int:alert_id>/ack', methods=['POST'])
def ack_alert(alert_id):
    try:
        db = current_app.config['DB']
        with db.get_conn() as conn:
            conn.execute("UPDATE intel_events SET acknowledged=1 WHERE id=?", (alert_id,))
        logger.info("Acknowledged alert %d", alert_id)
        return jsonify({'status': 'acknowledged'})
    except Exception as e:
        logger.exception("Error acknowledging alert %d", alert_id)
        return jsonify({'error': 'Internal server error'}), 500


@alert_bp.route('/ack-all', methods=['POST'])
def ack_all():
    try:
        db = current_app.config['DB']
        with db.get_conn() as conn:
            conn.execute("UPDATE intel_events SET acknowledged=1 WHERE acknowledged=0")
        logger.info("Bulk acknowledge: all alerts acknowledged")
        return jsonify({'status': 'all_acknowledged'})
    except Exception as e:
        logger.exception("Error acknowledging all alerts")
        return jsonify({'error': 'Internal server error'}), 500


@alert_bp.route('/rules', methods=['GET'])
def get_rules():
    try:
        db = current_app.config['DB']
        mgr = AlertManager(db)
        return jsonify({'rules': mgr.get_rules()})
    except Exception as e:
        logger.exception("Error getting alert rules")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("alert_routes module loaded")
