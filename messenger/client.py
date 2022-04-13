import argparse
import socket
import time
import sys
import os
import json
import dis
from json import JSONDecodeError
from metaclass import ClientVerifier

sys.path.append(os.path.join(os.getcwd(), '..'))
import log.config_client_log


from threading import Thread
from decors import log
from logging import getLogger
from common.utils import get_message, send_message
from common.variables import *
from errors import *

LOGGER = getLogger('client')


# Класс для формирования сообщений, их отправки на сервер и для взаимодействия с пользователем.
class ClientSender(Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    # Формирование и отправка сообщения на сервер.
    def create_message(self):
        to = input('Введите получателя сообщения: ')
        message = input('Введите сообщение: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            LOGGER.info(f'Отправлено сообщение для пользователя {to}')
        except:
            LOGGER.critical('Потеряно соединение с сервером.')
            exit(1)

    # Взаимодействия с пользователем
    def run(self):
        self.user_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.user_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.exit_message())
                except:
                    pass
                print('Завершение соединения.')
                LOGGER.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Неизвестная команда. help - вывести поддерживаемые команды.')

    # Функция выводящяя справку по использованию.
    def user_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение.')
        print('help - вывести информацию по командам')
        print('exit - выход из программы')


# Принимает сообщения с сервера и выводит их консоль.
class ClientReader(Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Функция приема сообщений и вывод их консоль. Завершается при потере соединения.
    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                LOGGER.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                LOGGER.critical(f'Потеряно соединение с сервером.')
                break


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
        receiver = ClientReader(client_name, transport)
        receiver.daemon = True
        receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        user_interface = ClientSender(client_name, transport)
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
