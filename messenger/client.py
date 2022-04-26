import argparse
import socket
import threading
import time
import sys
import os
import json
import dis
from json import JSONDecodeError
from metaclass import ClientVerifier
from client_database import ClientDatabase

sys.path.append(os.path.join(os.getcwd(), '..'))
import log.config_client_log

from threading import Thread
from decors import log
from logging import getLogger
from common.utils import get_message, send_message
from common.variables import *
from errors import *

LOGGER = getLogger('client')
socket_lock = threading.Lock()
database_lock = threading.Lock()


# Класс для формирования сообщений, их отправки на сервер и для взаимодействия с пользователем.
class ClientSender(Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
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

        with database_lock:
            if not self.database.check_user(to):
                LOGGER.error(f'Попытка отправить сообщение незарегистрированному пользователю {to}')
                return

        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')

        # Сохранение сообщения в истории
        with database_lock:
            self.database.save_message(self.account_name, to, message)

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with socket_lock:
            try:
                send_message(self.sock, message_dict)
                LOGGER.info(f'Отправлено сообщение для пользователя {to}')
            except OSError as err:
                if err.errno:
                    LOGGER.critical('Потеряно соединение с сервером.')
                    exit(1)
                else:
                    LOGGER.error('Не удалось передать сообщение. Таймаут соединения')

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
                with socket_lock:
                    try:
                        send_message(self.sock, self.exit_message())
                    except:
                        pass
                    print('Завершение соединения.')
                    LOGGER.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break

            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)

            elif command == 'edit':
                self.edit_contacts()

            elif command == 'history':
                self.print_history()

            else:
                print('Неизвестная команда. help - вывести поддерживаемые команды.')

    # Функция выводящяя справку по использованию.
    def user_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение.')
        print('history - история сообщений')
        print('contacts - список контактов')
        print('edit - редактирование списка контактов')
        print('help - вывести информацию по командам')
        print('exit - выход из программы')

    # Функция выводящяя историю сообщений
    def print_history(self):
        ask = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with database_lock:
            if ask == 'in':
                history_list = self.database.get_history(to_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} от {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(from_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} от {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(
                        f'\nСообщение от пользователя: {message[0]}, пользователю {message[1]} от {message[3]}\n{message[2]}')

    # Функция изменения контактов
    def edit_contacts(self):
        ans = input('Для удаления введите del, для добавления add: ')
        if ans == 'del':
            edit = input('Введите имя удаляемного контакта: ')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    LOGGER.error('Попытка удаления несуществующего контакта.')
        elif ans == 'add':
            # Проверка на дубликат создаваемого контакта
            edit = input('Введите имя создаваемого контакта: ')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with socket_lock:
                    try:
                        add_contact(self.sock, self.account_name, edit)
                    except ServerError:
                        LOGGER.error('Не удалось отправить информацию на сервер.')


# Принимает сообщения с сервера и выводит их консоль.
class ClientReader(Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    # Функция приема сообщений и вывод их консоль. Завершается при потере соединения.
    def run(self):
        while True:
            time.sleep(1)
            with socket_lock:
                try:
                    message = get_message(self.sock)

                # Принято некорректное сообщение
                except IncorrectDataRecivedError:
                    LOGGER.error(f'Не удалось декодировать полученное сообщение.')
                # Вышел таймаут соединения если errno = None, иначе обрыв соединения.
                except OSError as err:
                    if err.errno:
                        LOGGER.critical(f'Потеряно соединение с сервером.')
                        break

                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                    LOGGER.critical(f'Потеряно соединение с сервером.')
                    break

                # Если пакет корретно получен выводим в консоль и записываем в базу.
                else:
                    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                            and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                        print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                        # Захватываем работу с базой данных и сохраняем в неё сообщение
                        with database_lock:
                            try:
                                self.database.save_message(message[SENDER], self.account_name, message[MESSAGE_TEXT])
                            except:
                                LOGGER.error('Ошибка взаимодействия с базой данных')

                        LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    else:
                        LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


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


# Функция запрос контакт листа
def contacts_list_request(sock, name):
    LOGGER.debug(f'Запрос контакт листа для пользователся {name}')
    req = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER: name
    }
    LOGGER.debug(f'Сформирован запрос {req}')
    send_message(sock, req)
    ans = get_message(sock)
    LOGGER.debug(f'Получен ответ {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


# Функция добавления пользователя в контакт лист
def add_contact(sock, username, contact):
    LOGGER.debug(f'Создание контакта {contact}')
    req = {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Ошибка создания контакта')
    print('Удачное создание контакта.')


# Функция запроса списка доступных пользователей
def user_list_request(sock, username):
    LOGGER.debug(f'Запрос списка известных пользователей {username}')
    req = {
        ACTION: USERS_REQUEST,
        TIME: time.time(),
        ACCOUNT_NAME: username
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


# Функция удаления пользователя из контакт листа
def remove_contact(sock, username, contact):
    LOGGER.debug(f'Создание контакта {contact}')
    req = {
        ACTION: REMOVE_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Ошибка удаления клиента')
    print('Удачное удаление')


# Функция инициализации базы данных. Запускается при запуске и загружает данные с сервера.
def database_load(sock, database, username):
    # Загружаем список доступных пользователей
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        LOGGER.error('Ошибка запроса списка известных пользователей.')
    else:
        database.add_users(users_list)

    # Загружаем список контактов
    try:
        contacts_list = contacts_list_request(sock, username)
    except ServerError:
        LOGGER.error('Ошибка запроса списка контактов.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


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
    else:
        print(f'Клиентский модуль запущен с именем {client_name}')

    LOGGER.info(
        f'The client with the parameters is running: server address - {server_address}, '
        f'port - {server_port}, operating mode - {client_name}')

    # Инициализация сокета и сообщение серверу о появлении клиента
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Пауза 1 сек, для освобождения сокета
        transport.settimeout(1)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
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
        # Инициализация БД
        database = ClientDatabase(client_name)
        database_load(transport, database, client_name)

        # Если соединение с сервером установлено корректно, запускаем поток взаимодействия с пользователем
        module_sender = ClientSender(client_name, transport, database)
        module_sender.daemon = True
        module_sender.start()
        LOGGER.debug('Processes are running')

        # затем запускаем поток - приёмник сообщений.
        module_receiver = ClientReader(client_name, transport, database)
        module_receiver.daemon = True
        module_receiver.start()

        # Watchdog основной цикл, если один из потоков завершён значит потеряно соединение или пользователь ввёл exit.
        # Т.к. все события обработываются в потоках, просто завершаем цикл.
        while True:
            time.sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
