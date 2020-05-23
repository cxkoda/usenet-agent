from .UsenetAgent import UsenetAgent
from .EmailHandler import EmailHandler

import string
import datetime, time
import random

import logging

log = logging.getLogger(__name__)


class UsernetFarmAgent(UsenetAgent):
    hashDict = {
        'd582643efc080479fbff83bab3f9da66': 'ok',
        'd582643efc080479fbff83bab3f9da66': 'invalid_email',
        'af0dd8fd70f5bb562ab889b3a2153715': 'banned',
        '3003850bff8d1072651fde9063e33200': 'already_used_email'
    }

    def __init__(self, cfgHandler, serverName):
        log.info(f"Setting up UsernetFarmAgent for {serverName}")
        super(UsernetFarmAgent, self).__init__(cfgHandler, serverName)
        self.email = EmailHandler(self.cfg, serverName)

    def sendForm(self, mail):
        log.debug("Sending form")
        self.establishTorConnection()
        self.browser.open('https://usenet.farm/')
        form = self.browser.get_form()
        form['email'] = mail
        self.browser.submit_form(form)
        self.closeTorConnection()
        parsed = str(self.browser.parsed)
        toHash = parsed.splitlines()[1]
        htmlHash = self.hashString(toHash)

        try:
            log.debug(f'Response Hash: {htmlHash} -> {self.hashDict[htmlHash]}')
            if self.hashDict[htmlHash] == 'banned':
                raise Exception('Fuck!')
            elif self.hashDict[htmlHash] != 'ok':
                return False
        except KeyError:
            log.error(f'{toHash}')
            log.error(f'HTML Hash: {htmlHash} -> unknown !!')
            with open('farm-send-form-response.html', 'w') as html:
                html.write(parsed)
            raise Exception("Unknown response")

        return True

    def activateAccount(self, randomMail):
        while True:
            self.email.disconnect()
            self.email.connect()

            mail_text = self.email.fetchLatestMail(mailSubject="Activate your account",
                                                   sinceDate=datetime.date.today() - datetime.timedelta(1))

            activationLinkBegin = mail_text.find('Activate now') + 14

            link = mail_text[activationLinkBegin: activationLinkBegin + 272]
            link = ''.join(link.splitlines())

            log.info('Activation link found:' + link)
            break

        self.browser.open(link)
        parsed = str(self.browser.parsed)
        print(parsed)

    def getTrial(self):
        maxErrors = 20
        for n in range(maxErrors):
            randomMail = self.email.generateRandomMail(dotting=False)
            log.debug(f'Trial: {n}: {randomMail}')
            ok = self.sendForm(randomMail)


            ok = True

            if ok:
                break

        self.activateAccount(randomMail)
        username = 'user'
        password = 'pass'

        log.info(f'Account generated for {self.serverName} generated after {n} trials')
        log.debug(f'username: {username}')
        log.debug(f'password: {password}')
        self.updateSab(username, password)
        return True
