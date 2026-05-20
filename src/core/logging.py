"""
SupportTriagingEngine - Core Logging Utility
============================================

Overview
--------
This module provides centralized logging configuration for the
SupportTriagingEngine service. It ensures that all logs are formatted
consistently across the application and are written to both:

1. Standard output (`stdout`) for container-friendly observability
2. A persistent log file inside the `src/logs/` directory for tracing,
   debugging, and post-failure inspection

Key Features
------------
1. Dynamic Log Level Configuration
   - Reads the log level from global application settings
   - Defaults to INFO if the configured value is missing or invalid

2. Standardized Formatting
   - Uses a consistent structured log format:
     timestamp | level | logger name | message

3. Dual Output Handlers
   - Writes logs to `sys.stdout` for Docker/Kubernetes compatibility
   - Writes logs to a file so failures can be investigated later

4. Automatic Log Directory Creation
   - Ensures the `src/logs/` directory exists before writing logs

5. Duplicate Handler Protection
   - Prevents repeated logger configuration when `setup_logging()`
     is called multiple times

Usage
-----
Call `setup_logging()` once at the application entry point.
Use `get_logger(__name__)` within each module to retrieve a logger.

Example:
    from src.core.logging import setup_logging, get_logger

    setup_logging()
    logger = get_logger(__name__)
    logger.info("Application started")

Author
------
Elham Esmaeilnia (elham.e.shirvani@gmail.com)

Service
-------
SupportTriagingEngine

Version
-------
1.1.0

Date
----
2026-05-18
"""

import logging
import sys
from pathlib import Path


def setup_logging() -> None:
    """
    Initialize and configure the global logging system.

    This function configures the root logger with:
    - a log level loaded from application settings
    - a unified log message format
    - a stream handler that writes to stdout
    - a file handler that writes logs to `src/logs/engine_triage.log`

    The function also ensures the log directory exists before the file
    handler is created.

    To avoid duplicate log entries, this function first clears any
    existing handlers already attached to the root logger.

    Returns
    -------
    None
    """
    from src.core.config import settings

    log_dir = Path("src/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "engine_triage.log"

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()

    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Retrieve a logger instance for a specific module or component.

    This helper ensures all modules use the same centralized logging
    configuration established by `setup_logging()`.

    Parameters
    ----------
    name : str
        Name of the module or component, typically `__name__`.

    Returns
    -------
    logging.Logger
        A logger instance associated with the provided name.
    """
    return logging.getLogger(name)
