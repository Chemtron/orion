import hmac
import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from core.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


def _get_or_create_secret_key(data_dir):
    key_file = os.path.join(data_dir, '.secret_key')
    if os.path.exists(key_file):
        try:
            with open(key_file, 'r') as f:
                return f.read().strip()
        except Exception:
            pass
    key = os.urandom(32).hex()
    try:
        os.makedirs(data_dir, exist_ok=True)
        with open(key_file, 'w') as f:
            f.write(key)
    except Exception:
        pass
    return key


def create_app(config):
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or _get_or_create_secret_key(config.data_dir)
    app.config['ORION_CONFIG'] = config
    CORS(app, resources={r"/api/*": {"origins": os.environ.get('CORS_ORIGINS', 'http://127.0.0.1:5000').split(',')}})

    # Initialize database
    from core.database import Database
    db = Database(config.db_path)
    app.config['DB'] = db

    # Initialize scanner manager
    from scanners.scanner_manager import ScannerManager
    scanner_manager = ScannerManager(config, db)
    app.config['SCANNER'] = scanner_manager
    scanner_manager.start()

    # Register blueprints
    from api.scan_routes import scan_bp
    from api.device_routes import device_bp
    from api.intel_routes import intel_bp
    from api.enrichment_routes import enrichment_bp
    from api.settings_routes import settings_bp
    from api.alert_routes import alert_bp

    app.register_blueprint(scan_bp, url_prefix='/api/scan')
    app.register_blueprint(device_bp, url_prefix='/api/devices')
    app.register_blueprint(intel_bp, url_prefix='/api/intel')
    app.register_blueprint(enrichment_bp, url_prefix='/api/enrich')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(alert_bp, url_prefix='/api/alerts')

    # Register UI routes
    from api.ui_routes import ui_bp
    app.register_blueprint(ui_bp)

    # Rate limiter instance
    rate_limiter = RateLimiter()

    @app.before_request
    def security_checks():
        path = request.path

        # Skip all checks for UI routes (non-API)
        if not path.startswith('/api/'):
            return None

        # --- API Key Authentication ---
        api_key = os.environ.get('ORION_API_KEY', '')
        if api_key:
            provided = request.headers.get('X-API-Key', '')
            if not hmac.compare_digest(provided, api_key):
                logger.warning("Auth failure from %s", request.remote_addr)
                return jsonify({'error': 'Unauthorized'}), 401

        # --- CSRF Protection (mutating requests only) ---
        if request.method in ('POST', 'PUT', 'DELETE'):
            content_type = request.headers.get('Content-Type', '')
            if 'application/json' not in content_type:
                return jsonify({'error': 'Invalid Content-Type'}), 400

            origin = request.headers.get('Origin') or request.headers.get('Referer')
            if origin:
                server_origin = request.host_url.rstrip('/')
                if not origin.startswith(server_origin):
                    return jsonify({'error': 'Origin mismatch'}), 403
            else:
                if not app.config.get('TESTING'):
                    return jsonify({'error': 'Origin mismatch'}), 403

        # --- Rate Limiting ---
        client_ip = request.remote_addr
        if path.startswith('/api/scan/trigger'):
            if not rate_limiter.is_allowed(f'scan_trigger:{client_ip}', 10, 60):
                logger.warning("Rate limited: %s %s from %s", request.method, request.path, request.remote_addr)
                return jsonify({'error': 'Rate limit exceeded'}), 429
        elif path.startswith('/api/enrich'):
            if not rate_limiter.is_allowed(f'enrich:{client_ip}', 30, 60):
                logger.warning("Rate limited: %s %s from %s", request.method, request.path, request.remote_addr)
                return jsonify({'error': 'Rate limit exceeded'}), 429
        else:
            if not rate_limiter.is_allowed(f'api:{client_ip}', 120, 60):
                logger.warning("Rate limited: %s %s from %s", request.method, request.path, request.remote_addr)
                return jsonify({'error': 'Rate limit exceeded'}), 429

        return None

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        return response

    # JSON error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request'}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception("Unhandled exception")
        return jsonify({'error': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    from core.config import Config
    config = Config()
    app = create_app(config)
    print("App created successfully")
