#!/usr/bin/env python3

from UsenetAgent import HitnewsAgent


if __name__ == '__main__':
	with HitnewsAgent("config.ini", 'hitnews') as agent:
		agent.getTrial()
