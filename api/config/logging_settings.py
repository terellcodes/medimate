import os
import logging
from logging.config import dictConfig

from .settings import get_settings


def configure_logging() -> None:
    """Configure root and uvicorn loggers for the API service.

    The effective level is controlled by the `LOG_LEVEL` environment variable
    when present; otherwise it defaults to DEBUG when `settings.DEBUG` is True,
    and INFO otherwise.
    """
    try:
        settings = get_settings()
        default_level = "DEBUG" if settings.DEBUG else "INFO"
        log_level = os.getenv("LOG_LEVEL", default_level).upper()

        dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "()": "uvicorn.logging.DefaultFormatter",
                        "fmt": "%(levelname)s %(asctime)s %(name)s:%(lineno)d - %(message)s",
                    }
                },
                "handlers": {
                    "default": {
                        "class": "logging.StreamHandler",
                        "formatter": "default",
                    }
                },
                "root": {"level": log_level, "handlers": ["default"]},
                "loggers": {
                    "uvicorn": {"level": log_level, "handlers": ["default"], "propagate": False},
                    "uvicorn.error": {"level": log_level, "handlers": ["default"], "propagate": False},
                    "uvicorn.access": {"level": log_level, "handlers": ["default"], "propagate": False},
                },
            }
        )

        logging.getLogger(__name__).debug("Logging configured: level=%s", log_level)
    except Exception:
        # Avoid blocking startup on logging issues
        pass


