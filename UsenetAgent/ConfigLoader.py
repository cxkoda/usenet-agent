from configobj import ConfigObj
import os

import logging

log = logging.getLogger(__name__)


class ConfigLoader:
    @staticmethod
    def __doLoad(path):
        log.debug(f"Trying to load config from {path}")
        if os.path.exists(path):
            cfg = ConfigObj(path)
            log.info(f'Loaded config from {path}')
            return cfg
        else:
            return None

    @staticmethod
    def load(path=None):
        cfg = None
        if path is not None:
            cfg = ConfigLoader.__doLoad(path)

        if cfg is None:
            cfg = ConfigLoader.__doLoad('/config/config.ini')

        if cfg is None:
            cfg = ConfigLoader.__doLoad('./config.ini')

        return cfg
