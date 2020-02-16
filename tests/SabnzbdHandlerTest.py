import unittest

from UsenetAgent.SabnzbdHandler import SabnzbdHandler
from UsenetAgent.ConfigLoader import ConfigLoader


class SabnzbdHandlertest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SabnzbdHandlertest, self).__init__(*args, **kwargs)
        self.cfg = ConfigLoader.load('./config.ini')
        self.sab = SabnzbdHandler(self.cfg)

    def testAddServer(self):
        success = self.sab.addServer('hitnews', 'testusername', 'testpassword')
        self.assertEqual(success, True)


if __name__ == '__main__':
    unittest.main()
