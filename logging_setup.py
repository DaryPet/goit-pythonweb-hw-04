# import logging

# def setup_logging():
#     """Logger settings for the project"""
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
#     )
#     return logging.getLogger("async_file_sorter")

import logging
import sys


def setup_logging():
    """Настройка логгера для проекта"""
    logger = logging.getLogger("async_file_sorter")
    logger.setLevel(logging.INFO)

    # Создаем обработчик для вывода в консоль
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(handler)

    return logger
