#!/usr/bin/env python3

from usenetAgentLib import hitnewsAgent


if __name__ == '__main__':
	with hitnewsAgent("config.ini", 'hitnews') as agent:
		agent.getTrial()
