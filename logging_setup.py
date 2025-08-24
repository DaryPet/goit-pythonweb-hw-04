import logging
import sys


def setup_logging():
    """Settings for legging"""
    logger = logging.getLogger("async_file_sorter")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
