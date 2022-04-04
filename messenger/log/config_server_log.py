"""Кофнфигурация серверного логгера"""

import sys
import os
import logging
import logging.handlers

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import LOGGING_LEVEL

sys.path.append('../')


SERVER_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')


PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'data_logs', 'server.log')


STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D')
LOG_FILE.setFormatter(SERVER_FORMATTER)


LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)


if __name__ == '__main__':
    LOGGER.debug('DEBUG')
    LOGGER.info('INFO')
    LOGGER.error('ERROR')
    LOGGER.critical('CRITICAL')
    LOGGER.warning('WARNING')