import random
import string
import imaplib
import email

import logging

log = logging.getLogger(__name__)


class EmailHandler:
    def __init__(self, cfg):
        self.cfg = cfg

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

    def generateRandomMail(self, dottingStep=-1, addRandomString=True, randomString=None, identifier=""):
        if randomString is None:
            randomString = self.generateRandomString()

        randomMail = ''
        if dottingStep > 0:
            randomMail += self.dotString(self.cfg['MAIL']['name'], dottingStep)
        else:
            randomMail += self.cfg['MAIL']['name']

        if addRandomString:
            randomMail += self.cfg['MAIL']['extension_delimiter'] + identifier + '_' + randomString

        randomMail += '@' + self.cfg['MAIL']['domain']
        return randomMail

    def connect(self, ssl=True):
        address = self.cfg['MAIL']['imap_host']
        log.debug(f'Connecting to imap: {address}')
        try:
            if ssl:
                self.imapConnection = imaplib.IMAP4_SSL(address, 993)
            else:
                self.imapConnection = imaplib.IMAP4(address, 143)
        except Exception as e:
            log.error(e)
            return False

        try:
            self.imapConnection.login(self.cfg['MAIL']['login_user'], self.cfg['MAIL']['login_pass'])
        except Exception as e:
            log.error(e)
            return False

        ok, _ = self.imapConnection.select("inbox", readonly=True)
        return ok == 'OK'

    def disconnect(self):
        if hasattr(self, 'imapConnection'):
            self.imapConnection.close()
            del self.imapConnection

    def fetchLatestMail(self, mailSubject=None, sinceDate=None, recipient=None):
        if not hasattr(self, 'imapConnection'):
            self.connect()

        searchFilters = []
        if mailSubject is not None:
            searchFilters.append('HEADER Subject "%s"' % mailSubject)

        if sinceDate is not None:
            date = sinceDate.strftime("%d-%b-%Y")
            searchFilters.append('SENTSINCE {date}'.format(date=date))

        if recipient is not None:
            searchFilters.append(f'HEADER Delivered-To "{recipient}"')

        if searchFilters == []:
            searchCommand = 'ALL'
        else:
            searchCommand = '(' + ' '.join(searchFilters) + ')'

        log.debug(f"Fetching Latest mail with {searchCommand}")

        result, data = self.imapConnection.uid('search', None, searchCommand)

        inboxEmpty = (data[0] == b'')
        if inboxEmpty:
            return None

        latest_email_uid = data[0].split()[-1]
        result, data = self.imapConnection.uid('fetch', latest_email_uid, '(RFC822)')

        if result == "OK":
            body = data[0][1]
            msg = email.message_from_bytes(body)
            return msg
        else:
            return None
