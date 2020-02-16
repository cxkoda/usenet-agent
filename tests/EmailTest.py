import unittest
from UsenetAgent.EmailHandler import EmailHandler
from UsenetAgent.ConfigHandler import ConfigHandler


class EmailTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(EmailTest, self).__init__(*args, **kwargs)
        self.cfg = ConfigHandler('./').cfg
        self.email = EmailHandler(self.cfg, 'hitnews')

    def testConnection(self):
        success = self.email.connect()
        self.assertEqual(success, True)


if __name__ == '__main__':
    unittest.main()
