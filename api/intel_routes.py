import logging

from flask import Blueprint, jsonify, request, current_app
from intel.debrief_generator import DebriefGenerator

logger = logging.getLogger(__name__)

intel_bp = Blueprint('intel', __name__)


@intel_bp.route('/events', methods=['GET'])
def get_events():
    try:
        db = current_app.config['DB']
        try:
            limit = int(request.args.get('limit', 100))
        except ValueError:
            limit = 100
        unacked = request.args.get('unacked', 'false').lower() == 'true'
        events = db.get_intel_events(limit=limit, unacked_only=unacked)
        return jsonify({'events': events, 'count': len(events)})
    except Exception as e:
        logger.exception("Error getting intel events")
        return jsonify({'error': 'Internal server error'}), 500


@intel_bp.route('/events/<int:event_id>/ack', methods=['POST'])
def ack_event(event_id):
    try:
        db = current_app.config['DB']
        with db.get_conn() as conn:
            conn.execute("UPDATE intel_events SET acknowledged=1 WHERE id=?", (event_id,))
        logger.info("Acknowledged intel event %d", event_id)
        return jsonify({'status': 'acknowledged'})
    except Exception as e:
        logger.exception("Error acknowledging event %d", event_id)
        return jsonify({'error': 'Internal server error'}), 500


@intel_bp.route('/events/ack-all', methods=['POST'])
def ack_all_events():
    try:
        db = current_app.config['DB']
        with db.get_conn() as conn:
            conn.execute("UPDATE intel_events SET acknowledged=1 WHERE acknowledged=0")
        logger.info("Bulk acknowledge: all intel events acknowledged")
        return jsonify({'status': 'all_acknowledged'})
    except Exception as e:
        logger.exception("Error acknowledging all intel events")
        return jsonify({'error': 'Internal server error'}), 500


@intel_bp.route('/debrief', methods=['GET'])
def get_debrief():
    try:
        db = current_app.config['DB']
        try:
            window = int(request.args.get('window', 5))
        except ValueError:
            window = 5
        gen = DebriefGenerator(db)
        debrief = gen.generate(window_minutes=window)
        return jsonify(debrief)
    except Exception as e:
        logger.exception("Error generating debrief")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("intel_routes module loaded")
