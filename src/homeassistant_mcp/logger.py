import logging
import logging.handlers
import sys

def setup_logging() -> logging.Logger:
    """Configure logging with both console and file handlers."""
    logger = logging.getLogger("homeassistant_mcp")
    if logger.handlers:
        return logger  # already initialized, avoid adding duplicate handlers
    logger.setLevel(logging.DEBUG)

    log_file = "/tmp/homeassistant_mcp.log"

    # Log format: [%(levelname)s] %(asctime)s - %(name)s - %(message)s
    # Timestamp format: %Y-%m-%d %H:%M:%S
    log_format = "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Console Handler (to stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (RotatingFileHandler)
    # 1MB file size, 3 backup files
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=1048576,  # 1MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def get_logger(name: str | None = None):
    """
    Returns the root logger if name is None, otherwise returns a child logger.
    """
    if name is None:
        return logging.getLogger("homeassistant_mcp")
    
    # If name is __name__ like 'homeassistant_mcp.server', it's already a child
    # If it's something else, ensure it's a child of 'homeassistant_mcp'
    if not name.startswith("homeassistant_mcp"):
        return logging.getLogger(f"homeassistant_mcp.{name}")
    
    return logging.getLogger(name)
