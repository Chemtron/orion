#!/usr/bin/env python3
"""
ORION — Open Source Passive Signal Intelligence Platform
Entry point. Run with: python orion.py
"""
import sys
import os
import atexit

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.app import create_app
from core.config import Config
from core.logger import setup_logger

def main():
    config = Config()
    logger = setup_logger(config.log_level)
    logger.info("ORION v1.0.0 starting...")
    logger.info(f"Platform: {config.platform}")
    logger.info(f"Listening on {config.host}:{config.port}")

    app = create_app(config)
    atexit.register(app.config['SCANNER'].stop)
    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug,
        use_reloader=False,
        threaded=True
    )

if __name__ == '__main__':
    main()
