#!/usr/bin/env python3

import logging

log = logging.getLogger('main.UsernetAgent.Watchdog')

import sqlalchemy as sqla
import asyncio
from distutils.util import strtobool

from UsenetAgent.ConfigLoader import ConfigLoader
from UsenetAgent.Database import Database
from UsenetAgent.SabnzbdHandler import SabnzbdHandler
from UsenetAgent.EmailHandler import EmailHandler
from UsenetAgent.HitnewsAgent import HitnewsAgent
from UsenetAgent.UsenetFarmAgent import UsernetFarmAgent
from UsenetAgent.HostConfig import HostConfig
from UsenetAgent.UsenetAccount import UsenetAccount


class Environment:
    def __init__(self):
        self.cfg = ConfigLoader.load()
        self.db = Database(sqla.create_engine(f"sqlite:///{self.cfg['agent']['database']}"))
        self.sab = SabnzbdHandler(self.cfg)

        self.validateAccounts()
        self.accountsInUse = {}
        self.lock = asyncio.Lock()

    def validateAccounts(self):
        for acc in self.db.findValidConnections():
            host = self.getHost(acc.host)
            acc.valid = acc.checkLogin(host)
            self.db.session.add(acc)
        self.db.session.commit()

    def getHost(self, hostname):
        host = self.cfg['hosts'][hostname]
        try:
            host['ssl'] = strtobool(host['ssl'])
        except:
            pass
        return HostConfig(**host)

    def printInUse(self):
        for serverName, account in self.accountsInUse.items():
            log.info(f'{serverName}')
            log.info(f'  - {account}')

    def getAvailableAccount(self, hostname):
        self.validateAccounts()
        availableAccounts = [acc for acc in self.db.findValidConnections(hostname)
                             if acc not in self.accountsInUse.values()]
        if len(availableAccounts) > 0:
            return availableAccounts[0]
        else:
            return None


import abc


class Watchdog(abc.ABC):
    async def watch(self, account: UsenetAccount, action):
        await self.doWatch(account)
        action()

    @abc.abstractmethod
    async def doWatch(self, account: UsenetAccount):
        pass


class NNTPWatcher(Watchdog):
    def __init__(self, host, delay):
        self.host = host
        self.delay = delay

    async def doWatch(self, account):
        while True:
            await asyncio.sleep(self.delay)
            if not account.checkLogin(self.host):
                break


class Supervisor():
    def getUsenetAgent(self):
        if self.hostname == "Hitnews":
            email = EmailHandler(self.environment.cfg)
            return HitnewsAgent(email, 'asd')
        elif self.hostname == "UsenetFarm":
            email = EmailHandler(self.environment.cfg)
            return UsernetFarmAgent(email)
        else:
            raise Exception("Unknown Host, no Agent available")

    def __init__(self, environment: Environment, servername: str):
        self.environment = environment
        self.servername = servername
        self.hostname = environment.cfg['servers'][servername]['host']
        self.host = self.environment.getHost(self.hostname)
        self.account = None
        self.watchdogs = [NNTPWatcher(self.host, 60)]

    async def updateAccount(self):
        try:
            async with self.environment.lock:
                self.account = self.environment.getAvailableAccount(self.hostname)
                if self.account is not None:
                    self.environment.accountsInUse[self.servername] = self.account

            if self.account is None:
                agent = self.getUsenetAgent()
                account = agent.getTrial()
                account.host = self.hostname

            async with self.environment.lock:
                self.environment.db.session.add(self.account)
                self.environment.db.session.commit()

                self.environment.accountsInUse[self.servername] = self.account
                self.environment.sab.addServer(self.servername, self.account, self.host)
                self.environment.printInUse()

            return True
        except Exception:
            log.exception(f'Account generation for {self.servername} failed!')
            return False

    async def loop(self):
        while True:
            try:
                await self.startWatchdogs()
            except asyncio.CancelledError:
                pass
            finally:
                success = await self.updateAccount()

            if not success:
                log.critical(f'Terminating supervisor for {self.servername}')
                break

    async def startWatchdogs(self):
        if self.account is None:
            return

        assert (len(self.watchdogs) > 0)
        self.watchdogTasks = [asyncio.create_task(dog.watch(self.account, self.cancelWatchdogs)) for dog in
                              self.watchdogs]
        for task in self.watchdogTasks:
            await task

    def cancelWatchdogs(self):
        for task in self.watchdogTasks:
            task.cancel()
            del task


async def main():
    environment = Environment()
    tasks = []

    for servername in environment.cfg['servers']:
        supervisor = Supervisor(environment, servername)
        tasks.append(asyncio.create_task(supervisor.loop()))

    for task in tasks:
        await task


if __name__ == '__main__':
    asyncio.run(main())
