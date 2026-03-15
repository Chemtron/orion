import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


def setup_logger(level: str = 'INFO') -> logging.Logger:
    """Configure structured logging for ORION."""
    logger = logging.getLogger('orion')
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if logger.handlers:
        return logger

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console.setFormatter(fmt)
    logger.addHandler(console)

    # File handler
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'orion.log')
    try:
        file_handler = TimedRotatingFileHandler(
            log_file, when='midnight', backupCount=30, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file: {e}", file=sys.stderr)

    return logger


if __name__ == '__main__':
    log = setup_logger('DEBUG')
    log.info("Logger test")
    log.debug("Debug message")
    log.warning("Warning message")
