import logging

log = logging.getLogger(__name__)

from .UsenetAccount import UsenetAccount
from sqlalchemy.orm import sessionmaker

class Database:
    def __init__(self, engine):
        self.engine = engine
        UsenetAccount.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def getAllConnections(self):
        return self.session.query(UsenetAccount).order_by(UsenetAccount.id)

    def findValidConnections(self):
        return self.session.query(UsenetAccount).order_by(UsenetAccount.id).filter(UsenetAccount.valid)