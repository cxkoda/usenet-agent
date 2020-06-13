import requests
import logging
from distutils.util import strtobool
import json

log = logging.getLogger(__name__)

from .HostConfig import HostConfig
from .UsenetAccount import UsenetAccount


class SabnzbdHandler:
    def __init__(self, cfg):
        self.cfg = cfg

    def getConnectionAdapter(self):
        if strtobool(self.cfg['sabnzbd']['ssl']):
            return 'https://'
        else:
            return 'http://'

    def getApiAddress(self):
        adress = self.cfg['sabnzbd']['address']
        port = self.cfg['sabnzbd']['port']
        return self.getConnectionAdapter() + adress + ":" + port + "/api"

    def sendApiRequest(self, payload):
        localPayload = payload.copy()
        localPayload['apikey'] = self.cfg['sabnzbd']['apikey']
        return requests.get(self.getApiAddress(), params=localPayload)

    def checkResponse(self, response):
        if response.text.startswith('error'):
            log.error(response.text)
            return False
        else:
            return True

    def addServer(self, serverName: str, account: UsenetAccount, hostConfig: HostConfig):
        payload = {
            'mode': 'set_config',
            'section': 'servers',
            'name': serverName,
            'host': hostConfig.url,
            'port': hostConfig.port,
            'ssl': int(hostConfig.ssl),
            'username': account.username,
            'password': account.password,
            'connections': hostConfig.connections
        }
        log.debug(f'Adding server {payload}')
        try:
            response = self.sendApiRequest(payload)
        except requests.exceptions.RequestException as e:
            log.error(e)
            return False

        return self.checkResponse(response)

    def restart(self):
        log.info('Restarting')
        payload = {
            'mode': 'restart',
            'output': 'xml'
        }
        try:
            response = self.sendApiRequest(payload)
        except requests.exceptions.RequestException as e:
            log.error(e)
            return False

        return self.checkResponse(response)

    def getServers(self):
        payload = {
            'mode': 'get_config',
            'section': 'servers',
            'output': 'json',
        }
        log.debug(f'Adding server {payload}')
        response = self.sendApiRequest(payload)
        self.checkResponse(response)

        return json.loads(response.text)['config']['servers']