from UsenetAgent.AgentFactory import getUsenetAgent
from UsenetAgent.ConfigLoader import ConfigLoader

if __name__ == '__main__':
    cfg = ConfigLoader.load()
    for serverName in cfg['servers']:
        host = cfg['servers'][serverName]['host']
        agent = getUsenetAgent(host, cfg, serverName)

        if agent is None:
            continue
        else:
            agent.getTrial()
