from .UsenetAgent import UsenetAgent
from .EmailHandler import EmailHandler

import string
import datetime, time
import random

import logging

log = logging.getLogger(__name__)


class HitnewsAgent(UsenetAgent):
    def __init__(self, cfgHandler, serverName):
        log.info(f"Setting up HitnewsAgent for {serverName}")
        super(HitnewsAgent, self).__init__(cfgHandler, serverName)
        self.hashDict = {
            'bb1cd48c90192510bc15281a5a353e8b': 'ok',
            '2f5079bb3ba571927d49f00ec4374b50': 'invalid_email',
            '8404dff87117eb65e316a6aa7a6171dd': 'invalid_email',
            '98746b4749692ce29d7cda5855a70105': 'already_used_email'
        }

        self.email = EmailHandler(self.cfg, serverName)

    def generateRandomString(self, size=10, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def sendForm(self, mail, username, password):
        log.debug("Sending form")
        self.browser.open('https://member.hitnews.com/signup.php')
        form = self.browser.get_form()
        form['name_f'] = self.generateRandomString(10, string.ascii_lowercase)
        form['name_l'] = self.generateRandomString(10, string.ascii_lowercase)
        form['email'] = mail
        form['login'] = username
        form['pass0'] = password
        form['pass1'] = password
        self.browser.submit_form(form)
        parsed = str(self.browser.parsed)

        # self.writeFile('hitnews_after_form.html', parsed)

        htmlHash = self.hashString(parsed.splitlines()[128])

        try:
            log.debug(f'Response Hash: {htmlHash} -> {self.hashDict[htmlHash]}')
            if self.hashDict[htmlHash] != 'ok':
                return False
        except KeyError:
            log.error(f'HTML Hash: {htmlHash} -> unknown !!')
            with open('hitnews-send-form-response.html', 'w') as html:
                html.write(parsed)
            return False

        log.debug('Agreeing to 2nd Form...')
        form = self.browser.get_form()
        form['i_agree'].value = ['1']
        self.browser.submit_form(form)

        # self.writeFile('hitnews_after_accepting.html', parsed)

        return True

    def activateAccount(self, randomMail):
        while True:
            self.email.disconnect()
            self.email.connect()

            mail_text = self.email.fetchLatestMail(mailSubject="Hitnews.com - Account Activation",
                                                   sinceDate=datetime.date.today() - datetime.timedelta(1))

            recipientBegin = mail_text.find('Delivered-To:') + 14
            recipient = mail_text[recipientBegin: recipientBegin + len(randomMail)]

            if recipient != randomMail:
                time.sleep(1)
                continue

            link_begin = mail_text.find('https://member.hitnews.com/signup.php?cs=')
            link = mail_text[link_begin:link_begin + 61]

            log.info('Activation link found:' + link)
            break

        self.browser.open(link)
        parsed = str(self.browser.parsed)

        # self.writeFile('hitnews_after_activation.html', parsed)

    def getTrial(self):
        n = 0
        consequent_errors = 0
        while True:
            n += 1
            username = self.generateRandomString()
            password = self.generateRandomString()
            randomMail = self.email.generateRandomMail(dotting=False)
            log.debug(f'Trial: {n}: {randomMail}')

            if self.sendForm(randomMail, username, password):
                break

            if (consequent_errors > 20):
                return False
            else:
                consequent_errors += 1

        self.activateAccount(randomMail)

        log.info(f'Account generated for {self.serverName} generated after {n} trials')
        log.debug(f'username: {username}')
        log.debug(f'password: {password}')
        self.updateSab(username, password)
        return True
