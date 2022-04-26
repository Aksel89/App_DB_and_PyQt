import logging
import sys

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func):

    def log_save(*args, **kwargs):
        LOGGER.debug(f'Function called: {func.__name__} with parameters {args}, {kwargs}'                     
                     f'Calling from the module: {func.__module__}')
        result = func(*args, **kwargs)
        return result
    return log_save
