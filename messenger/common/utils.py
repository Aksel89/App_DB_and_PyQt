import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from errors import *


def get_message(client):
    """
    Функция принимает и декодирует сообщения. Сообщение принимает в байтах --> выдает словарь.
    При приеме любого другого типа данных возвращает ошибку значения.
    :param client:
    :return:
    """
    encoding_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoding_response, bytes):
        json_response = encoding_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        else:
            raise IncorrectDataRecivedError
    else:
        raise IncorrectDataRecivedError


def send_message(sock, message):
    """
    Функция кодирует и отправляет сообщение.
    Принимает словарь и отправляет его.
    :param sock:
    :param message:
    :return:
    """
    if not isinstance(message, dict):
        raise NonDictInputError

    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
