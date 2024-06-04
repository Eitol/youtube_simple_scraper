import logging
import sys


def build_default_logger() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Cree un manejador para enviar los mensajes al stdout
    handler = logging.StreamHandler(sys.stdout)

    # Puede establecer el nivel del manejador si lo desea
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
