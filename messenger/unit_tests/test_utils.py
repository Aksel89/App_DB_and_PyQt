import unittest
import json
import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..'))

from common.utils import send_message, get_message
from common.variables import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, ENCODING


class TestSocket:

    """
    Тестирование отправки и получения сообщений.
    """

    def __init__(self, dict_message):
        self.dict_message = dict_message
        self.encoding_message = None
        self.received_message = None

    def send(self, sending_message):
        """
        Тестирование отправки сообщения
        :param sending_message:
        :return:
        """
        json_message = json.dumps(self.dict_message)
        self.encoding_message = json_message.encode(ENCODING)
        self.received_message = sending_message

    def recv(self, max_connections):
        """
        Получение данных из сокета
        :param max_connections:
        :return:
        """
        json_message = json.dumps(self.dict_message)
        return json_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    """
    Тестирование основных функций
    """
    test_message = {
        ACTION: PRESENCE,
        TIME: 1645387814,
        USER: {ACCOUNT_NAME: 'test'},
    }
    good_response = {RESPONSE: 200}
    bad_response = {
        RESPONSE: 400,
        ERROR: 'error',
    }

    def test_send_message_good(self):

        test_socket = TestSocket(self.test_message)
        send_message(test_socket, self.test_message)
        self.assertEqual(test_socket.encoding_message, test_socket.received_message)

    def test_send_message_bad(self):

        test_socket = TestSocket(self.test_message)
        send_message(test_socket, self.test_message)
        self.assertRaises(Exception, send_message, 'wrong dictionary')

    def test_get_message_good(self):

        test_socket_ok = TestSocket(self.good_response)
        self.assertEqual(get_message(test_socket_ok), self.good_response)

    def test_get_message_bad(self):

        test_socket_bad = TestSocket(self.bad_response)
        self.assertEqual(get_message(test_socket_bad), self.bad_response)


if __name__ == '__main__':
    unittest.main()
