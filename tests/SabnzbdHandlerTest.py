import unittest

from UsenetAgent.SabnzbdHandler import SabnzbdHandler
from UsenetAgent.ConfigHandler import ConfigHandler


class SabnzbdHandlertest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SabnzbdHandlertest, self).__init__(*args, **kwargs)
        self.cfg = ConfigHandler('./').cfg
        self.sab = SabnzbdHandler(self.cfg)

    def testAddServer(self):
        success = self.sab.addServer('test', 'testusername', 'testpassword')
        self.assertEqual(success, True)


if __name__ == '__main__':
    unittest.main()
