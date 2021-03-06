#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import sqlalchemy as sqla
from configobj import ConfigObj
from distutils.util import strtobool

from UsenetAgent.ConfigLoader import ConfigLoader
from UsenetAgent.Database import Database
from UsenetAgent.SabnzbdHandler import SabnzbdHandler
from UsenetAgent.EmailHandler import EmailHandler
from UsenetAgent.HitnewsAgent import HitnewsAgent
from UsenetAgent.UsenetFarmAgent import UsernetFarmAgent
from UsenetAgent.HostConfig import HostConfig


def getUsenetAgent(cfg, hostname):
    if hostname == "Hitnews":
        email = EmailHandler(cfg)
        return HitnewsAgent(email)
    elif hostname == "UsenetFarm":
        email = EmailHandler(cfg)
        return UsernetFarmAgent(email)
    else:
        raise Exception("Unknown Host, no Agent available")


def getHost(cfg, hostname):
    host = cfg['hosts'][hostname]
    try:
        host['ssl'] = strtobool(host['ssl'])
    except:
        pass
    return HostConfig(**host)


def main():
    cfg = ConfigLoader.load()
    db = Database(sqla.create_engine(f"sqlite:///{cfg['agent']['database']}"))
    sab = SabnzbdHandler(cfg)

    for acc in db.findValidConnections():
        host = getHost(cfg, acc.host)
        acc.valid = acc.checkLogin(host)
        db.session.add(acc)
    db.session.commit()

    accountsInUse = set()

    for serverName in cfg['servers']:
        try:
            hostname = cfg['servers'][serverName]['host']
            host = getHost(cfg, hostname)

            availableAccounts = [acc for acc in db.findValidConnections(hostname)
                                 if acc not in accountsInUse]

            if len(availableAccounts) > 0:
                account = availableAccounts[0]
            else:
                agent = getUsenetAgent(cfg, hostname)
                account = agent.getTrial()
                account.host = hostname

                db.session.add(account)
                db.session.commit()

            accountsInUse.add(account)
            sab.addServer(serverName, account, host)
        except Exception:
            log.exception(f'Account generation for {serverName} failed!')


if __name__ == '__main__':
    main()
