from .UsenetAgent import UsenetAgent
from .EmailHandler import EmailHandler
from .HostConfig import HostConfig
from .utils import retry

import io
import json
import re

import logging

log = logging.getLogger(__name__)


class UsernetFarmAgent(UsenetAgent):
    def __init__(self, cfgHandler, agentName):
        log.info(f"Setting up UsernetFarmAgent for {agentName}")
        defaultHostConfig = HostConfig(host="news.usenet.farm", ssl=True, connections=40)
        super(UsernetFarmAgent, self).__init__(cfgHandler, agentName, defaultHostConfig)
        self.email = EmailHandler(self.cfg)

    def checkFormResponse(self, response):
        hashDict = {
            '927cebcb8a0b52a93a2810a9cf88bba3': 'ok',
            'd582643efc080479fbff83bab3f9da66': 'invalid_email',
            'af0dd8fd70f5bb562ab889b3a2153715': 'banned',
            '3003850bff8d1072651fde9063e33200': 'already_used_email'
        }

        toHash = response.splitlines()[1]
        htmlHash = self.hashString(toHash)

        try:
            log.debug(f'Response Hash: {htmlHash} -> {hashDict[htmlHash]}')
            if hashDict[htmlHash] == 'banned':
                raise Exception('Fuck!')
            elif hashDict[htmlHash] == 'ok':
                return True
            else:
                return False
        except KeyError:
            log.error(f'{toHash}')
            log.error(f'HTML Hash: {htmlHash} -> unknown !!')
            with open('farm-send-form-response.html', 'w') as html:
                html.write(response)
            raise Exception("Unknown response")

    def sendForm(self, mail, withTor=False):
        log.debug("Sending form")

        if withTor:
            self.establishTorConnection()

        self.browser.open('https://usenet.farm/')
        form = self.browser.get_form()
        form['email'] = mail
        self.browser.submit_form(form)

        if withTor:
            self.closeTorConnection()

        response = str(self.browser.parsed)
        ok = self.checkFormResponse(response)
        return ok

    def activateAccount(self, randomMail):
        def getActivationMail():
            mail_text = self.email.fetchLatestMail(mailSubject="Activate your account", recipient=randomMail)
            return mail_text is not None, mail_text

        mail_text = retry(getActivationMail, maxretries=20, timeout=1)
        mail_text = str(mail_text).replace('=\n', '', -1)

        link = re.search("\[!Activate now\]\((.*?)\)", mail_text).group(0)
        link = link.split('(')[-1][:-1]

        # Cut away the first 3D after uuid=..
        link = link.replace('=3D', '=', -1)

        log.info(f'Activation link found: {link}')

        self.browser.open(link)
        parsed = str(self.browser.parsed)

        with open('farm-activation-response.html', 'w') as html:
            html.write(parsed)

        return parsed

    def getCredentials(self, randomMail):
        def getActivationMail():
            mail_text = self.email.fetchLatestMail(mailSubject="Activated your trial account", recipient=randomMail)
            return mail_text is not None, None

        retry(getActivationMail, maxretries=20, timeout=1)

        self.browser.open("https://usenet.farm/action/config/userpass")
        data = json.load(io.BytesIO(self.browser.response.content))

        return data["user"], data["pass"]

    def getTrial(self):
        def doFillAndSend():
            randomMail = self.email.generateRandomMail(identifier=self.agentName)
            success = self.sendForm(randomMail)
            return success, randomMail

        randomMail = retry(doFillAndSend, maxretries=10)
        self.activateAccount(randomMail)
        username, password = self.getCredentials(randomMail)

        log.info(f'Account generated for {self.agentName}')
        log.debug(f'username: {username}')
        log.debug(f'password: {password}')
        self.updateSab(username, password)
        return True
