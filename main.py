#!/usr/bin/env python3

from UsenetAgent.AgentFactory import getUsenetAgent
from UsenetAgent.ConfigLoader import ConfigLoader


def main():
    cfg = ConfigLoader.load()
    for agentName in cfg['servers']:
        host = cfg['servers'][agentName]['host']
        agent = getUsenetAgent(host, cfg, agentName)

        if agent is None:
            continue
        else:
            agent.getTrial()


if __name__ == '__main__':
    main()
