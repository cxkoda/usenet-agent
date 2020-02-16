import unittest
from UsenetAgent.EmailHandler import EmailHandler
from UsenetAgent.ConfigLoader import ConfigLoader


class EmailTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(EmailTest, self).__init__(*args, **kwargs)
        self.cfg = ConfigLoader.load('./config.ini')
        self.email = EmailHandler(self.cfg, 'hitnews')

    def testConnection(self):
        success = self.email.connect()
        self.assertEqual(success, True)


if __name__ == '__main__':
    unittest.main()
