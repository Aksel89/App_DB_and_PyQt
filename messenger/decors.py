import sys
import logging
import log.config_client_log
import log.config_server_log


if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func):

    def log_save(*args, **kwargs):
        result = func(*args, **kwargs)
        LOGGER.debug(f'Function called: {func.__name__} with parameters {args}, {kwargs}'                     
                     f'Calling from the module: {func.__module__}')
        return result
    return log_save
