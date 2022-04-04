import argparse
import socket
import time
import sys
import os
from json import JSONDecodeError

sys.path.append(os.path.join(os.getcwd(), '..'))
import log.config_client_log


from threading import Thread
from decors import log
from logging import getLogger
from common.utils import get_message, send_message
from common.variables import *
from errors import *

LOGGER = getLogger('client')


@log
def create_exit_message(account_name):

    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def message_from_server(sock, username):
    """
    Функция обрабатывает сообщения других пользователей
    :param message:
    :return:
    """
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and SENDER in message \
                    and DESTINATION in message and message[DESTINATION] == username:
                print(f'Получено сообщение от {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                LOGGER.info(f'Received a message from {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            else:
                LOGGER.error(f'An incorrect message was received from the server: {message}')

        except IncorrectDataRecivedError:
            LOGGER.error(f'The received message could not be decoded.')

        except(OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, JSONDecodeError):
            LOGGER.critical(f'Connection to the server is lost')
            break


@log
def create_message(sock, account_name='Guest'):
    """
    Функция запрашивает имя получателяя сообщения и само сообщение,
    после этого отправляет данные на сервер.
    """
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение или "exit" для завершения работы: ')

    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'The message dictionary has been formed: {message_dict}')
    try:
        send_message(sock, message_dict)
        LOGGER.info(f'The message was sent to the user {to_user}')
    except Exception as e:
        print(e)
        LOGGER.critical('Connection to the server is lost')
        sys.exit(1)


def print_help():
    """Функция выводящяя справку по использованию"""
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@log
def user_interactive(sock, username):
    """
    Функция, принимает от пользователя команды и обрабатывает их.
    :param sock:
    :param username:
    :return:
    """
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            LOGGER.info("Completion of work on the user's command.")
            # Задержка, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробуйте снова. help - вывести поддерживаемые команды.')


@log
def create_presence(account_name='Guest'):
    """
    Функция генерирует запрос о присутствии  клиента
    :param account_name:
    :return:
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        },
        'encoding': ENCODING,
    }
    LOGGER.info(f'Create message: {PRESENCE} from user {account_name}')
    return out


@log
def process_ans(answer):
    """
    Функция разбирает ответ сервера
    :param answer:
    :return:
    """
    LOGGER.debug(f'Server response: {answer}')
    if RESPONSE in answer:
        if answer[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {answer[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():

    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Attempt to launch a client with an incorrect port number: {server_port}. '
            f'Valid addresses are 1024 to 65535. The client is being terminated.')
        sys.exit(1)

    # Проверим допустим ли выбранный режим работы клиента
    if client_mode not in ('listen', 'send'):
        LOGGER.critical(f'Invalid operation mode is specified {client_mode}, '
                        f'Acceptable modes: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    """
    Функция работы через командную строку.
    client.py -p < номер порта в диапазоне [1024-65535} > -a < IP адрес клиента >
    Если нет параметров - используются параметры, заданные по-умолчанию
    :return:
    """
    server_address, server_port, client_name = arg_parser()

    """
    Сообщение о запуске.
    """
    print(f'Консольный чат. Клиентский модуль. Имя пользователя {client_name}')

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    LOGGER.info(
        f'The client with the parameters is running: server address - {server_address}, '
        f'port - {server_port}, operating mode - {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence())
        answer = process_ans(get_message(transport))
        LOGGER.info(f'A connection to the server has been established. Server response: {answer}')
        print(f'Установлено соединение с сервером.')
    except JSONDecodeError:
        LOGGER.error('The received JSON string could not be decoded.')
        sys.exit(1)
    except ServerError as error:
        LOGGER.error(f'When establishing a connection, the server returned an error: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        LOGGER.error(f'The required field is missing in the server response {missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(
            f'Failed to connect to the server {server_address}:{server_port}, '
            f'the destination computer rejected the connection request.')
        sys.exit(1)
    else:
        # Если соединение с сервером установлено корректно,
        # запускаем клиентский процесс приёма сообщений
        receiver = Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        user_interface = Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        LOGGER.debug('Запущены процессы')

        # Watchdog основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
