import os
import logging


def get_logger(name: str):
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(LOGLEVEL)

    for handler in logging.getLogger().handlers:
        handler.setLevel(LOGLEVEL)

    return logging.getLogger(name)