import unittest
import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..'))

from client import create_presence, process_ans
from common.variables import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, ENCODING, BAD_REQUEST


class TestClient(unittest.TestCase):
    """
    Тесты клиента.
    """

    def test_create_presence(self):
        """
        Корректность запроса.
        :return:
        """
        test = create_presence()
        test[TIME] = 1645387814
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1645387814, USER: {ACCOUNT_NAME: 'Guest'}, 'encoding': ENCODING})

    def test_200_ok(self):

        self.assertEqual(process_ans({RESPONSE: 200}), '200 : OK')

    def test_400_bad(self):

        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'BAD_REQUEST'}), f'400 : {BAD_REQUEST}')

    def test_server_error(self):

        self.assertRaises(ValueError, process_ans, {ERROR: 'error'})


if __name__ == '__main__':
    unittest.main()
