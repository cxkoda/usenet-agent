from configobj import ConfigObj
import os
import logging

log = logging.getLogger(__name__)

class ConfigHandler:
    def __init__(self, path=None):
        if path is not None:
            self.loadConfigFiles(path)
        else:
            self.getFromPrimary()

    def loadConfigFiles(self, path):
        cfgPath = path + '/config.ini'
        if os.path.exists(cfgPath):
            self.cfg = ConfigObj(cfgPath)
            self.db = ConfigObj(path + '/db.ini')
            log.info(f'Using config from {path}')
            return True
        else:
            return False

    def getFromPrimary(self):
        return self.loadConfigFiles('/config')
