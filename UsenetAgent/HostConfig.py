import logging

log = logging.getLogger(__name__)


class HostConfig:
    def __init__(self, host, port=None, ssl=True, connections=10):
        if port is None:
            if ssl is True:
                port = 563
            else:
                port = 119
        self.host = host
        self.port = port
        self.ssl = ssl
        self.connections = connections
