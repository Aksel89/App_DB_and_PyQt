import unittest
import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..'))

from server import process_client_message
from common.variables import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, ENCODING, RESPONDEFAULT_IP_ADDRESSE


class TestServer(unittest.TestCase):
    """
    Тесты функций сервера.
    """
    error_dict = {
        RESPONDEFAULT_IP_ADDRESSE: 400,
        ERROR: 'BAD REQUEST'
    }
    correct_dict = {RESPONSE: 200}

    def test_correct_message(self):

        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1645387814, USER: {ACCOUNT_NAME: 'Guest'}, 'encoding': ENCODING}),
            self.correct_dict)

    def test_error_action_message(self):

        self.assertEqual(process_client_message(
            {TIME: 1645387814, USER: {ACCOUNT_NAME: 'Guest'}, 'encoding': ENCODING}),
            self.error_dict,
        )

    def test_incorrect_action_message(self):

        self.assertEqual(process_client_message(
            {ACTION: 'any action', TIME: 1645387814, USER: {ACCOUNT_NAME: 'Guest'}, 'encoding': ENCODING}),
            self.error_dict)

    def test_message_time_error(self):

        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}, 'encoding': ENCODING}), self.error_dict)

    def test_message_user_error(self):

        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1645387814, 'encoding': ENCODING}), self.error_dict)

    def test_unregistered_user_message(self):

        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1645387814, USER: {ACCOUNT_NAME: 'test'}, 'encoding': ENCODING}), self.error_dict)


if __name__ == '__main__':
    unittest.main()
