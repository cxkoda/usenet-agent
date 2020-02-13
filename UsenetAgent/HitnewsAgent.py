from .UsenetAgent import usenetAgent

import string
import datetime, time
import logging

log = logging.getLogger(__name__)

class HitnewsAgent(usenetAgent):
	def __init__(self, cfgPath, sabHostName='hitnews'):
		super(HitnewsAgent, self).__init__(cfgPath, 'hitnews', sabHostName)

	def sendForm(self, mail, username, password):
		log.info("Sending form")
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

		self.writeFile('hitnews_after_form.html', parsed)

		htmlHash = self.hashString(parsed.splitlines()[128])

		try:
			log.info('Response Hash:', htmlHash, "->", self.hashDict[htmlHash])
			if self.hashDict[htmlHash] != 'ok':
				return False
		except KeyError:
			log.info('HTML Hash:', htmlHash, "->", "unknown !!")
			return False

		log.info('Agreeing to 2nd Form...')
		form = self.browser.get_form()
		form['i_agree'].value = ['1']
		self.browser.submit_form(form)

		self.writeFile('hitnews_after_accepting.html', parsed)

		return True


	def activateAccount(self):
		self.establishImapConnection()

		while(True):
			mail_text = self.fetchLatestMail(mailSubject="Hitnews.com - Account Activation",
											 sinceDate=datetime.date.today()-datetime.timedelta(1))
			link_begin = mail_text.find('https://member.hitnews.com/signup.php?cs=')
			link = mail_text[link_begin:link_begin + 61]

			if (link != self.cfg[self.sabHostName]['activation_link']):
				self.cfg[self.sabHostName]['activation_link'] = link
				log.info('Activation link found:' + link)
				break
			else:
				time.sleep(1)

		self.browser.open(link)
		parsed = str(self.browser.parsed)

		self.writeFile('hitnews_after_activation.html', parsed)


	def getTrial(self):
		n = 0
		consequent_errors = 0
		while True:
			n += 1
			log.info(f'Trial: {n}')
			self.setHostUsername(self.generateRandomString())
			self.setHostPassword(self.generateRandomString())
			step = self.getDottingStep()
			self.generateDottedMail(step)
			if self.sendForm(self.randomMail, self.hostUsername, self.hostPassword):
				break

			if (consequent_errors > 20):
				return False
			else:
				consequent_errors += 1

		time.sleep(10)
		self.activateAccount()

		self.printCredentials()
		self.updateSab()
		return True