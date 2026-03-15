import logging

from flask import Blueprint, render_template, current_app

logger = logging.getLogger(__name__)

ui_bp = Blueprint('ui', __name__)


@ui_bp.route('/')
@ui_bp.route('/hud')
def hud():
    return render_template('hud.html')


@ui_bp.route('/timeline')
def timeline():
    return render_template('timeline.html')


@ui_bp.route('/devices')
def devices():
    return render_template('devices.html')


@ui_bp.route('/enrichment')
def enrichment():
    return render_template('enrichment.html')


@ui_bp.route('/settings')
def settings():
    return render_template('settings.html')


@ui_bp.route('/alerts')
def alerts():
    return render_template('alerts.html')


@ui_bp.route('/debrief')
def debrief():
    return render_template('debrief.html')


if __name__ == '__main__':
    print("ui_routes module loaded")
