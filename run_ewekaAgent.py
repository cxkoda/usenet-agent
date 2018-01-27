from usenetAgentLib import ewekaAgent


if __name__ == '__main__':
	with ewekaAgent("config.ini", 'eweka') as agent:
		agent.getTrial()