import hashlib
import io
import logging
import platform
import random
import string
import subprocess

import imaplib
import requests
import socket
import socks
import stem.process
from robobrowser import RoboBrowser

from .SabnzbdHandler import SabnzbdHandler

log = logging.getLogger(__name__)

class UsenetAgent:
    def __init__(self, cfgHandler, serverName):
        self.cfg = cfgHandler.cfg
        self.sab = SabnzbdHandler(self.cfg)
        self.serverName = serverName

        self.mailAddress = self.cfg['MAIL']['name'] + '@' + self.cfg['MAIL']['domain']
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
        self.socksPort = int(self.cfg['bot']['torPort'])

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

    def generateRandomString(self, size=10, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def dotString(self, str, step=None, maxDotting=1):
        if step is not None:
            ret = ''.join(str[i] + '.' if (int(step / 2 ** i)) % 2 == 1 else str[i] for i in range(len(str) - 1))
            return ret + str[-1]
        else:
            nBetweens = len(str) - 1
            selection = ['', '.']
            dots = [''.join(random.choice(selection) for _ in range(maxDotting)) for _ in range(nBetweens)]

            ret = ''
            for i in range(nBetweens):
                ret += str[i] + dots[i]

            ret += str[-1]

            return ret

    def getDottingStep(self):
        try:
            self.dottingStep = int(self.cfg['servers'][self.serverName]['dotting_step'])
        except:
            self.dottingStep = 1
        self.cfg['servers'][self.serverName]['dotting_step'] = self.dottingStep + 1
        self.cfg.write()
        return self.dottingStep

    def generateDottedMail(self, step):
        self.randomMail = self.dotString(self.cfg['MAIL']['name'], step=step) + '@' + self.cfg['MAIL']['domain']
        return self.randomMail

    def generateRandomMail(self, dotting=True, addRandomString=True, randomString=None, **kwargs):
        if randomString is None:
            randomString = self.generateRandomString()

        self.randomMail = ''

        if dotting:
            self.randomMail += self.dotString(self.cfg['MAIL']['name'], **kwargs)
        else:
            self.randomMail += self.cfg['MAIL']['name']

        if addRandomString:
            self.randomMail += '+' + self.serverName + '_' + randomString

        self.randomMail += '@' + self.cfg['MAIL']['domain']
        return self.randomMail

    def setHostUsername(self, username=None):
        if username is None:
            username = self.generateRandomString()
        self.hostUsername = username

    def setHostPassword(self, password=None):
        if password is None:
            password = self.generateRandomString()
        self.hostPassword = password

    def printCredentials(self):
        log.info(f'username: {self.hostUsername}')
        log.info(f'password: {self.hostPassword}')

    def hashString(self, parsed):
        return hashlib.md5(parsed.encode()).hexdigest()

    def establishImapConnection(self, ssl=True):
        print('Connecting to mailserver via IMAP')
        if ssl:
            self.imapConnection = imaplib.IMAP4_SSL(self.cfg['MAIL']['imap_host'], 993)
        else:
            self.imapConnection = imaplib.IMAP4(self.cfg['MAIL']['imap_host'], 143)
        self.imapConnection.login(self.cfg['MAIL']['login_user'], self.cfg['MAIL']['login_pass'])
        self.imapConnection.select("inbox")

    def closeImapConnection(self):
        self.imapConnection.close()
        del self.imapConnection

    def fetchLatestMail(self, mailSubject=None, sinceDate=None):
        if not hasattr(self, 'imapConnection'):
            self.establishImapConnection()

        searchFilters = []
        if mailSubject is not None:
            searchFilters.append('HEADER Subject "%s"' % mailSubject)

        if sinceDate is not None:
            date = sinceDate.strftime("%d-%b-%Y")
            searchFilters.append('SENTSINCE {date}'.format(date=date))

        if searchFilters == []:
            searchCommand = 'ALL'
        else:
            searchCommand = '(' + ' '.join(searchFilters) + ')'

        result, data = self.imapConnection.uid('search', None, searchCommand)

        latest_email_uid = data[0].split()[-1]
        result, data = self.imapConnection.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        return str(raw_email)

    def writeFile(self, fileName, parsedString):
        with io.open(fileName, 'w+', encoding='utf-8') as file:
            file.write(parsedString)
            
    def updateSab(self):
        self.sab.addServer(self.serverName, self.hostUsername, self.hostPassword)
