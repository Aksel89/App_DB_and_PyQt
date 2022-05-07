import logging
import sys

if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


# Дескриптор для описания порта:
class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(
                f'Попытка запуска сервера с некорректным портом {value}. Допустимы адреса с 1024 до 65535.')
            raise TypeError('Некорректный номер порта')
        # Если порт прошел проверку, добавляем его в список атрибутов экземпляра
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
