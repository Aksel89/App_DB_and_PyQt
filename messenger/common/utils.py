import json
import sys

sys.path.append('../')
from common.variables import *
from common.errors import *
from common.decors import log


@log
def get_message(client):
    """
    Функция принимает и декодирует сообщения. Сообщение принимает в байтах -->
    выдает словарь. При приеме любого другого типа данных возвращает
    ошибку значения.
    :param client:
    :return:
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    json_response = encoded_response.decode(ENCODING)
    response = json.loads(json_response)
    if isinstance(response, dict):
        return response
    else:
        raise TypeError


@log
def send_message(sock, message):
    '''
    Функция отправки словарей через сокет.
    Кодирует словарь в формат JSON и отправляет через сокет.
    :param sock: сокет для передачи
    :param message: словарь для передачи
    :return: ничего не возвращает
    '''
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
