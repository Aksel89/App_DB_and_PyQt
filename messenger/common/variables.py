"""
Конфигурационный файл с необходимыми переменными
"""
import logging

# Порт по умолчанию
DEFAULT_PORT = 7777
# IP адрес по умолчанию
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальное количество подключений
MAX_CONNECTIONS = 5
# Максимальная длина сообщения (байт)
MAX_PACKAGE_LENGTH = 1024
# Кодировка
ENCODING = 'utf-8'


# Ключи для JIM протокола
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'ACCOUNT_NAME'
SENDER = 'sender'
DESTINATION = 'to'


# Служебные ключи подключений
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
ALERT = 'alert'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
RESPONDEFAULT_IP_ADDRESSE = 'respondefault_ip_addresse'
BAD_REQUEST = 'BAD_REQUEST'

# Уровень логирования
LOGGING_LEVEL = logging.DEBUG

# Ответы сервера
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}