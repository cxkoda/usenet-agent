from .UsenetAgent import UsenetAgent
from .UsenetAccount import UsenetAccount
from .utils import retry

import io
import json
import re

import logging

log = logging.getLogger(__name__)

from .EmailHandler import EmailHandler

class UsernetFarmAgent(UsenetAgent):
    def __init__(self, emailHandler: EmailHandler):
        log.info(f"Setting up UsernetFarmAgent")
        super(UsernetFarmAgent, self).__init__()
        self.email = emailHandler

    def checkFormResponse(self, response):
        if response.find("You got mail!") >= 0:
            return True
        elif response.find("Sorry, reached maxretries!") >= 0:
            raise Exception("Banned from UsenetFarm")
        elif response.find("Sorry, We have banned you due to abuse.") >= 0:
            raise Exception("Banned from UsenetFarm")
        else:
            dumpFileName = 'farm-send-form-response.html'
            log.error(f'Dumping html to {dumpFileName}')
            with open(dumpFileName, 'w') as html:
                html.write(response)
            raise Exception("Unknown response")



    def sendForm(self, randomMail, withTor=False, dryRun=False):
        log.debug(f'Sending form for {randomMail}')

        if dryRun:
            with open('farm-send-form-response.html', 'r') as file:
                response = file.read()
        else:
            if withTor:
                self.establishTorConnection()

            self.browser.open('https://usenet.farm/')
            form = self.browser.get_form()
            form['email'] = randomMail
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

        mail_text = retry(getActivationMail, maxretries=30, timeout=2)
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

        retry(getActivationMail, maxretries=30, timeout=2)

        self.browser.open("https://usenet.farm/action/config/userpass")
        data = json.load(io.BytesIO(self.browser.response.content))

        return data["user"], data["pass"]

    def getTrial(self):
        def doFillAndSend():
            randomMail = self.email.generateRandomMail(identifier="UsenetFarm")
            success = self.sendForm(randomMail)
            return success, randomMail

        randomMail = retry(doFillAndSend, maxretries=10)
        self.activateAccount(randomMail)
        username, password = self.getCredentials(randomMail)
        account = UsenetAccount(username=username, password=password, valid=True)

        log.info(f'Account generated for UsenetFarm using {randomMail}')
        log.debug(f'{account}')

        return account
