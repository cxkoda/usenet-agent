from .UsenetAgent import UsenetAgent
from .EmailHandler import EmailHandler

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


import re

import logging

log = logging.getLogger(__name__)


class UsernetFarmAgent(UsenetAgent):
    def __init__(self, cfgHandler, serverName):
        log.info(f"Setting up UsernetFarmAgent for {serverName}")
        super(UsernetFarmAgent, self).__init__(cfgHandler, serverName)
        self.email = EmailHandler(self.cfg, serverName)

        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)

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
            if self.hashDict[htmlHash] == 'banned':
                raise Exception('Fuck!')
            elif self.hashDict[htmlHash] == 'ok':
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
        mail_text = None
        while mail_text is None:
            mail_text = self.email.fetchLatestMail(mailSubject="Activate your account",
                                                   recipient=randomMail)

        mail_text = mail_text.as_string()
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
        mail_text = None
        while mail_text is None:
            mail_text = self.email.fetchLatestMail(mailSubject="Activated your trial account",
                                                   recipient=randomMail)

        mail_text = mail_text.as_string()
        mail_text = str(mail_text).replace('=\n', '', -1)

        link = re.search("\[!Config assistant\]\((.*?)\)", mail_text).group(0)
        link = link.split('(')[-1][:-1]

        # Cut away the first 3D after uuid=..
        link = link.replace('=3D', '=', -1)

        log.info(f'Config link found: {link}')

        # Since this part requires javascript we have to use selenium
        self.driver.get(link)

        button = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.LINK_TEXT, 'SabNZBd')))
        button.click()

        configTable = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))

        config = {}
        for line in configTable.text.split("\n"):
            entry = line.split(' ')
            config[entry[0]] = entry[1]

        return config["Username"], config["Password"]

    def getTrial(self):
        maxErrors = 20
        for n in range(maxErrors):
            randomMail = self.email.generateRandomMail(dotting=False)
            log.debug(f'Trial: {n}: {randomMail}')
            ok = self.sendForm(randomMail)

            if ok:
                break

        self.activateAccount(randomMail)
        username, password = self.getCredentials(randomMail)

        log.info(f'Account generated for {self.serverName} generated after {n} trials')
        log.debug(f'username: {username}')
        log.debug(f'password: {password}')
        self.updateSab(username, password)
        return True
