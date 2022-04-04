import socket
import sys
import json
import argparse
import select
import time
import os
from common.variables import *
from common.utils import get_message, send_message
from logging import getLogger

sys.path.append(os.path.join(os.getcwd(), '..'))
import log.config_server_log

from decors import log

LOGGER = getLogger('server')


@log
def process_client_message(message, messages_list, client, clients, names):
    """
    Функция принимает и обрабатывает сообщения от клиента в виде словаря.
    Проверяет корректность и возвращает ответ для клиента в виде словаря.
    :param message:
    :return:
    """
    LOGGER.debug(f'Check message from client: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:

        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
        # Если это сообщение, то добавляем его в очередь сообщений.
        # Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message \
        and TIME in message and SENDER in message and MESSAGE_TEXT in message:
            messages_list.append(message)
            return
    # Если клиент выходит
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    # Иначе отдаём Bad request
    else:
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректен.'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
    :param message:
    :param names:
    :param listen_socks:
    :return:
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        LOGGER.info(f'A message has been sent to the user {message[DESTINATION]} '
                    f'from the user {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        LOGGER.error(
            f'User {message[DESTINATION]} is not registered on the server, '
            f'sending a message is not possible.')


@log
def arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        LOGGER.critical(
            f'Attempt to start the server with the wrong port '
            f'{listen_port}. Addresses from 1024 to 65535 are allowed.')
        sys.exit(1)

    return listen_address, listen_port


@log
def main():
    listen_address, listen_port = arg_parser()

    LOGGER.info(
        f'The server is running, the port for connections: {listen_port}, '
        f'the address from which connections are accepted: {listen_address}. '
        f'If the address is not specified, connections from any addresses are accepted.')

    # Готовим сокет
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    # список клиентов , очередь сообщений
    clients = []
    messages = []

    # Словарь пользователей и их сокеты
    names = dict()  # {client_name: client_socket}

    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)
    # Основной цикл программы сервера
    while True:
        # Ждём подключения, если таймаут вышел, ловим исключение.
        try:
            client, client_address = transport.accept()
        except OSError as err:
            print(err.errno)  # The error number returns None because it's just a timeout
            pass
        else:
            LOGGER.info(f'A connection has been established with {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Проверяем на наличие ждущих клиентов
        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # принимаем сообщения и если ошибка, исключаем клиента.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message, clients, names)
                except Exception:
                    LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(client_with_message)

        # Если есть сообщения, обрабатываем каждое.
        for i in messages:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()


if __name__ == "__main__":
    main()
