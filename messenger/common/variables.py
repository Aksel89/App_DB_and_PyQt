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
# База данных сервера
SERVER_CONFIG = 'server.ini'


# Ключи для JIM протокола
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'ACCOUNT_NAME'
SENDER = 'sender'
DESTINATION = 'to'
DATA = 'bin'
PUBLIC_KEY = 'pubkey'

# Служебные ключи подключений
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
ALERT = 'alert'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'
RESPONDEFAULT_IP_ADDRESSES = 'respondefault_ip_addresses'
BAD_REQUEST = 'BAD_REQUEST'
PUBLIC_KEY_REQUEST = 'pubkey_need'

# Уровень логирования
LOGGING_LEVEL = logging.DEBUG


# Ответы сервера
RESPONSE_200 = {RESPONSE: 200}

RESPONSE_202 = {
    RESPONSE: 202,
    LIST_INFO: None
}

RESPONSE_205 = {
    RESPONSE: 205
}

RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}

RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}
