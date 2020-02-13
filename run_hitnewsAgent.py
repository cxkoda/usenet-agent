#!/usr/bin/env python3

from UsenetAgent.HitnewsAgent import HitnewsAgent
from UsenetAgent.ConfigHandler import ConfigHandler


if __name__ == '__main__':
	cfgHandler = ConfigHandler('./config')
	with HitnewsAgent(cfgHandler, 'hitnews') as agent:
		agent.getTrial()
