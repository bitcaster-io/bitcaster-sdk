import logging
import sys

logger = logging.getLogger("bitcaster_sdk")


def configure_api() -> None:
    h = logging.StreamHandler(sys.stdout)
    h.flush = sys.stdout.flush  # type: ignore[method-assign]
    logger.addHandler(h)


def configure_cli() -> None:
    h = logging.NullHandler()
    logger.addHandler(h)
