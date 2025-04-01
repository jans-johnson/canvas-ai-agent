import sys
from datetime import datetime
import os

from loguru import logger as _logger

from app.config import PROJECT_ROOT, SHOW_LOGS


_print_level = "INFO"


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    """Adjust the log level to above level"""
    global _print_level
    _print_level = print_level

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d%H%M%S")
    log_name = (
        f"{name}_{formatted_date}" if name else formatted_date
    )  # name a log with prefix name

    _logger.remove()
    
    # Only add stderr handler if SHOW_LOGS is True
    if SHOW_LOGS:
        _logger.add(sys.stderr, level=print_level)
    
    # Always add file logging regardless of SHOW_LOGS setting
    # Make sure logs directory exists
    logs_dir = PROJECT_ROOT / "logs"
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
    
    _logger.add(logs_dir / f"{log_name}.log", level=logfile_level)
    return _logger


logger = define_log_level()


if __name__ == "__main__":
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
