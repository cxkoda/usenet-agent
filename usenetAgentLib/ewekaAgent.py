from .usenetAgent import usenetAgent
from robobrowser import RoboBrowser
import io
from stem.util import term

class ewekaAgent(usenetAgent):
	def __init__(self, cfgPath, sabHostName='eweka'):
		super(ewekaAgent, self).__init__(cfgPath, 'eweka', sabHostName)

	def sendForm(self, mail):
		print('Random Trial Mail: %s' % mail)

		browser = RoboBrowser(history=True)
		browser.open('https://www.eweka.nl/en/free_trial/')
		form = browser.get_form()
		form['email'].value = mail
		browser.submit_form(form)
		parsed = str(browser.parsed)

		with io.open('last_response.html', 'w+', encoding='utf-8') as htmlFile:
			htmlFile.write(parsed)

		htmlHash = self.hashString(parsed)
		hashFlag = False

		try:
			print('Response Hash:', htmlHash, "->", self.hashDict[htmlHash])
		except KeyError:
			print('HTML Hash:', htmlHash, "->", "INTERESTING !!")
			hashFlag = True
			exit(0)


		if parsed.find('Password') > 0 or parsed.find('password') > 0 or parsed.find('Pass') > 0 or parsed.find('pass') > 0:
			print('Robo Success')

			start = parsed.find('Password:</i>') + 82
			len = 6
			password = parsed[start:start+len]
			self.setHostPassword(password)

			with io.open('last_response.html', 'w+', encoding='utf-8') as htmlFile:
				htmlFile.write(parsed)

			return True

		return False


	def getTrial(self):
		n = 0
		consequent_errors = 0
		while True:
			n += 1
			try:
				self.closeTorConnection()
			except:
				pass
			try:
				print(term.format('Trial: %s' % n, term.Color.YELLOW))
				self.establishTorConnection()
				self.testConnection()
				self.generateRandomMail()
				self.setHostUsername(self.randomMail)
				if self.sendForm(self.randomMail):
					break
				self.closeTorConnection()
				consequent_errors = 0
			except:
				if (consequent_errors > 20):
					return False
				else:
					consequent_errors += 1

		self.printCredentials()
		self.writeCfgFiles()
		self.sabHandler.restart()
		return True