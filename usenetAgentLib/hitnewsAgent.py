from .usenetAgent import usenetAgent
from robobrowser import RoboBrowser
import io, string
import datetime, time
from stem.util import term

class hitnewsAgent(usenetAgent):
	def __init__(self, cfgPath, sabHostName='hitnews'):
		super(hitnewsAgent, self).__init__(cfgPath, 'hitnews', sabHostName)

	def sendForm(self, mail, username, password):
		print("Sending form")
		browser = RoboBrowser(history=True)
		browser.open('https://member.hitnews.com/signup.php')
		form = browser.get_form()
		form['name_f'] = self.generateRandomString(10, string.ascii_lowercase)
		form['name_l'] = self.generateRandomString(10, string.ascii_lowercase)
		form['email'] = mail
		form['login'] = username
		form['pass0'] = password
		form['pass1'] = password
		browser.submit_form(form)
		parsed = str(browser.parsed)

		htmlHash = self.hashString(parsed.splitlines()[107])

		try:
			print('Response Hash:', htmlHash, "->", self.hashDict[htmlHash])
			if self.hashDict[htmlHash] != 'ok':
				return False
		except KeyError:
			print('HTML Hash:', htmlHash, "->", "unknown !!")
			return False


		with io.open('hitnews_after_form.html', 'w+', encoding='utf-8') as htmlFile:
			htmlFile.write(parsed)

		print('Agreeing to 2nd Form...')
		form = browser.get_form()
		form['i_agree'].value = ['1']
		browser.submit_form(form)

		with io.open('hitnews_after_accepting.html', 'w+', encoding='utf-8') as htmlFile:
			htmlFile.write(parsed)

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
				print('Activation link found:' + link)
				break
			else:
				time.sleep(1)

		browser = RoboBrowser(history=True)
		browser.open(link)
		parsed = str(browser.parsed)

		with io.open('hitnews_after_activation.html', 'w+', encoding='utf-8') as htmlFile:
			htmlFile.write(parsed)


	def getTrial(self):
		n = 0
		consequent_errors = 0
		while True:
			n += 1
			print(term.format('Trial: %s' % n, term.Color.YELLOW))
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
		self.writeCfgFiles()
		self.sabHandler.restart()
		return True