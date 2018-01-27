from stem.util import term
import stem.process
import os, platform, signal
import socks, socket

import requests
from robobrowser import RoboBrowser

import imaplib

import datetime, time
import string
import random

import hashlib
import subprocess
import io


from configobj import ConfigObj

class sabnzbdHandler:
	def __init__(self, cfg):
		self.cfg = cfg
		cfgSabnzbdPath = os.getenv(self.cfg['sabnzbd'][platform.system()]['start_dir']) + \
						 self.cfg['sabnzbd'][platform.system()]['inipath']
		self.cfgSabnzbd = ConfigObj(cfgSabnzbdPath)

	def syncSabnzbdEntry(self, cfgHostName, sabHostName):
		try:
			self.cfgSabnzbd['servers'][sabHostName]['username'] = self.cfg[cfgHostName]['username']
			self.cfgSabnzbd['servers'][sabHostName]['password'] = self.cfg[cfgHostName]['password']
		except:
			self.cfgSabnzbd['servers'][sabHostName] = dict(self.cfg[cfgHostName])

		self.cfgSabnzbd.write()

	def restart(self):
		SabRestart = 'http://127.0.0.1:8080/api?mode=restart&output=xml&apikey=' + self.cfgSabnzbd['misc']['api_key']
		try:
			requests.get(SabRestart)
		except requests.exceptions.RequestException:
			pass

class usedIPList:
	def __init__(self, filePath):
		self.usedIpsCFG = ConfigObj(filePath)
		self.usedIps = {}

		for key, value in self.usedIpsCFG.items():
			self.usedIps[key] = value.split(' ')

	def write(self):

		self.usedIpsCFG.write()





class usenetAgent:
	def __init__(self, cfgPath, cfgHostName, sabHostName):
		self.cfg = ConfigObj(cfgPath)
		self.sabHandler = sabnzbdHandler(self.cfg)

		self.cfgHostName = cfgHostName
		self.sabHostName = sabHostName

		self.mailAddress = self.cfg['MAIL']['name'] + '@' + self.cfg['MAIL']['domain']

		try:
			pass
		except:
			self.usedIpList = None

		self.hashDict = {}
		for key, value in self.cfg[self.cfgHostName]['md5_hashes'].items():
			self.hashDict[value] = key

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.closeTorConnection()
		self.cfg.write()

	def closeTorConnection(self):
		if hasattr(self, 'torProcess'):
			print('Killing Tor Process', self.torProcess.pid)
			self.torProcess.kill()

	def establishTorConnection(self):
		def print_bootstrap_lines(line):
			if "Bootstrapped " in line:
				print(term.format(line, term.Color.BLUE))

		self.torProcess = stem.process.launch_tor_with_config(
			config = {
				'SocksPort': str(self.socksPort),
			},
			init_msg_handler = print_bootstrap_lines)
		socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", self.socksPort)
		socket.socket = socks.socksocket
		self.getIP()

	def getIP(self):
		self.ip = requests.get('http://icanhazip.com').text.split('\n')[0]

	def testConnection(self):
		self.getIP()
		print(term.format('Request IP: %s' % self.ip, term.Color.GREEN))

	def addUsedIp(self):
		pass

	def generateRandomString(self, size=10, chars=string.ascii_lowercase + string.digits):
		return ''.join(random.choice(chars) for _ in range(size))

	def dotString(self, str, step=None):
		if step is None:
			step = random.randint(0, 2**(len(str)-1))
		ret = ''.join(str[i] + '.' if int(step / 2 ** i) % 2 == 1 else str[i] for i in range(len(str) - 1))
		return ret + str[-1]

	def generateRandomMail(self, dotting=True, addRandomString=True, randomString = None):
		if randomString is None:
			randomString = self.generateRandomString()

		self.randomMail = ''

		if dotting:
			self.randomMail += self.dotString(self.cfg['MAIL']['name'])
		else:
			self.randomMail += self.cfg['MAIL']['name']

		if addRandomString:
			self.randomMail += '+' + self.cfgHostName + '_' + randomString

		self.randomMail += '@' + self.cfg['MAIL']['domain']
		return self.randomMail

	def setHostUsername(self, username = None):
		if username is None:
			username = self.generateRandomString()
		self.hostUsername = username

	def setHostPassword(self, password = None):
		if password is None:
			password = self.generateRandomString()
		self.hostPassword = password

	def printCredentials(self):
		print(term.format(self.hostUsername, term.Color.GREEN))
		print(term.format(self.hostPassword, term.Color.GREEN))

	def writeCfgFiles(self):
		self.cfg[self.cfgHostName]['username'] = self.hostUsername
		self.cfg[self.cfgHostName]['password'] = self.hostPassword
		self.cfg[self.cfgHostName]['generated'] = datetime.datetime.strftime(datetime.datetime.now(), '%a %d-%m-%Y %H:%M:%S')
		self.cfg[self.cfgHostName]['worked'] = 0
		self.cfg.write()
		self.sabHandler.syncSabnzbdEntry(self.cfgHostName, self.sabHostName)



class ewekaAgent(usenetAgent):
	def __init__(self, cfgPath, sabHostName='eweka'):
		super(ewekaAgent, self).__init__(cfgPath, 'eweka', sabHostName)

	def sendForm(self, mail):
		print('Random Trial Mail: %s' % mail)
		#response = requests.post('https://www.eweka.nl/en/free_trial/', data={'email': mail})
		#parsed = response.text
		#soup = BeautifulSoup(response.content, 'html.parser')

		browser = RoboBrowser(history=True)
		browser.open('https://www.eweka.nl/en/free_trial/')
		form = browser.get_form()
		form['email'].value = mail
		browser.submit_form(form)
		parsed = str(browser.parsed)

		with io.open('last_response.html', 'w+', encoding='utf-8') as htmlFile:
			htmlFile.write(parsed)

		#with open('res.html', 'r') as htmlFile:
		#	parsed = htmlFile.read()

		htmlHash = hashlib.md5(parsed.encode()).hexdigest()
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
					exit(1)
				else:
					consequent_errors += 1

		self.printCredentials()
		self.writeCfgFiles()
		self.sabHandler.restart()
		return True



if __name__ == '__main__':
	consequent_errors = 0
	with ewekaAgent("config.ini", 'eweka') as ua:
			ua.getTrial()