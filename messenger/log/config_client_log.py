"""
Конфигурация сбора логов клиента.
"""

import sys
import os
import logging

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import LOGGING_LEVEL


CLIENT_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')


PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'data_logs', 'client.log')


STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
LOG_FILE = logging.FileHandler(PATH, encoding='utf8')
LOG_FILE.setFormatter(CLIENT_FORMATTER)


LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)


if __name__ == '__main__':
    LOGGER.debug('DEBUG')
    LOGGER.info('INFO')
    LOGGER.error('ERROR')
    LOGGER.critical('CRITICAL')
    LOGGER.warning('WARNING')

