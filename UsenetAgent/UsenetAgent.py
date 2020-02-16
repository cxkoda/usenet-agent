import hashlib
import io
import platform
import subprocess

import requests
import socket
import socks
import stem.process
from robobrowser import RoboBrowser

from .SabnzbdHandler import SabnzbdHandler

import logging

log = logging.getLogger(__name__)


class UsenetAgent:
    def __init__(self, cfg, serverName):
        self.cfg = cfg
        self.sab = SabnzbdHandler(cfg)
        self.serverName = serverName

        self.browser = RoboBrowser(history=True, parser="html5lib")

        try:
            pass
        except:
            self.usedIpList = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeTorConnection()
        self.cfg.write()

    def closeTorConnection(self):
        if (platform.system() == 'Windows'):
            subprocess.Popen(["taskkill", "/IM", "tor.exe", "/F"])
            if hasattr(self, 'torProcess'):
                del self.torProcess
        else:
            if hasattr(self, 'torProcess'):
                log.info('Killing Tor Process', self.torProcess.pid)
                self.torProcess.kill()
                del self.torProcess

    def establishTorConnection(self):
        self.socksPort = int(self.cfg['agent']['torPort'])

        def print_bootstrap_lines(line):
            if "Bootstrapped " in line:
                log.info(line)

        self.torProcess = stem.process.launch_tor_with_config(
            config={
                'SocksPort': str(self.socksPort),
            },
            init_msg_handler=print_bootstrap_lines)
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", self.socksPort)
        socket.socket = socks.socksocket
        self.getIP()

    def getIP(self):
        self.ip = requests.get('http://icanhazip.com').text.split('\n')[0]

    def testConnection(self):
        self.getIP()
        log.info(f'Request IP: {self.ip}')

    def addUsedIp(self):
        pass

    def hashString(self, parsed):
        return hashlib.md5(parsed.encode()).hexdigest()

    def writeFile(self, fileName, parsedString):
        with io.open(fileName, 'w+', encoding='utf-8') as file:
            file.write(parsedString)

    def updateSab(self, username, password):
        self.sab.addServer(self.serverName, username, password)
