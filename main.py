from UsenetAgent.AgentFactory import getUsenetAgent
from UsenetAgent.ConfigHandler import ConfigHandler

if __name__ == '__main__':
    cfgHandler = ConfigHandler('./config')
    for serverName in cfgHandler.cfg['servers']:
        host = cfgHandler.cfg['servers'][serverName]['host']
        agent = getUsenetAgent(host, cfgHandler, serverName)

        if agent is None:
            continue
        else:
            agent.getTrial()
