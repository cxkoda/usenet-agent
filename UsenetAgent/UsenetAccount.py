import logging

log = logging.getLogger(__name__)

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
import nntplib

from .HostConfig import HostConfig

Base = declarative_base()


class UsenetAccount(Base):
    __tablename__ = 'UsenetAccount'

    id = Column(Integer, primary_key=True)
    host = Column(String)
    username = Column(String)
    password = Column(String)
    valid = Column(Boolean, default=False)

    def __str__(self):
        return f"<UsenetAccount(id={self.id}, host={self.host}, username={self.username}, password={self.password}, valid={self.valid})>"

    def __repr__(self):
        print(str(self))

    def checkLogin(self, host: HostConfig):
        if host.ssl:
            connector = nntplib.NNTP_SSL
        else:
            connector = nntplib.NNTP

        try:
            connector(host.url, port=host.port, user=self.username, password=self.password)
        except nntplib.NNTPError:
            return False

        return True
