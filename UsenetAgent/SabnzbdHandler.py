import requests
import logging
from distutils.util import strtobool

log = logging.getLogger(__name__)


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

    def addServer(self, serverName, username, password):
        log.debug(f'Adding server {serverName}')
        payload = {
            'mode': 'set_config',
            'section': 'servers',
            'name': serverName,
            'username': username,
            'password': password,
            'connections': 5
        }
        try:
            response = self.sendApiRequest(payload)
        except requests.exceptions.RequestException as e:
            log.error(e)

        self.checkResponse(response)
        return response


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

        self.checkResponse(response)
        return response
