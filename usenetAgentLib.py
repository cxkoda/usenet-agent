from stem.util import term
import stem.process
import os, platform, signal
import socks, socket

import datetime, time
import requests
import string
import random
from configobj import ConfigObj

class sabConfigurator:
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
		SabRestart = 'http://localhost:8080/api?mode=restart&output=xml&apikey=' + self.cfgSabnzbd['misc']['api_key']
		try:
			requests.get(SabRestart)
		except requests.exceptions.RequestException:
			pass



class usenetAgent:
	def __init__(self, cfgPath, cfgHostName, sabHostName):
		self.cfg = ConfigObj(cfgPath)
		self.sabCfg = sabConfigurator(self.cfg)

		self.cfgHostName = cfgHostName
		self.sabHostName = sabHostName

		self.socksPort = 9050

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
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

	def testConnection(self):
		print(requests.get('http://icanhazip.com').text)

	def generateRandomString(self, size=10, chars=string.ascii_lowercase + string.digits):
		return ''.join(random.choice(chars) for _ in range(size))

	def generateRandomMail(self, randomString = None):
		if randomString is None:
			randomString = self.generateRandomString()
		self.randomMail = self.cfg['MAIL']['name'] + '+' \
						  + self.cfgHostName + '_' \
						  + randomString \
						  + '@' + self.cfg['MAIL']['domain']
		return self.randomMail

	def setHostUsername(self, username = None):
		if username is None:
			username = self.generateRandomString()
		self.HostUsername = username

	def setHostPassword(self, password = None):
		if password is None:
			password = self.generateRandomString()
		self.HostPassword = password

	def writeCfgFiles(self):
		self.cfg[self.cfgHostName]['username'] = self.HostUsername
		self.cfg[self.cfgHostName]['password'] = self.HostPassword
		self.cfg[self.cfgHostName]['generated'] = datetime.datetime.strftime(datetime.datetime.now(), '%a %d-%m-%Y %H:%M:%S')
		self.cfg[self.cfgHostName]['worked'] = 0
		self.cfg.write()
		self.sabCfg.syncSabnzbdEntry(self.cfgHostName, self.sabHostName)



class ewekaAgent(usenetAgent):
	def __init__(self, cfgPath, sabHostName='eweka'):
		super(ewekaAgent, self).__init__(cfgPath, 'eweka', sabHostName)

	def sendForm(self, mail):
		response = requests.post('https://www.eweka.nl/en/free_trial/', data={'email': mail})
		#response = requests.get('https://www.eweka.nl/en/free_trial')
		print(mail)
		html_file = open('res.html', 'w+')
		html_file.write(response.text)
		html_file.close()

	def getTrial(self):
		self.generateRandomMail()
		self.setHostUsername(self.randomMail)
		self.sendForm(self.randomMail)




if __name__ == '__main__':
	with ewekaAgent("config.ini") as ua:
		ua.establishTorConnection()
		ua.testConnection()
		ua.getTrial()