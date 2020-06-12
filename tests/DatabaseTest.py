import unittest

import sqlalchemy as sqla
from UsenetAgent.Database import Database
from UsenetAgent.UsenetAccount import UsenetAccount


class DatabaseTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(DatabaseTest, self).__init__(*args, **kwargs)

        engine = sqla.create_engine('sqlite:///:memory:')
        self.database = Database(engine)

        # Add some test data
        self.database.session.add(UsenetAccount(
            host="aaasdsd.asd.de", username="user1", password="pass1", valid=False
        ))
        self.database.session.add(UsenetAccount(
            host="aaasdsd.asd.de", username="user2", password="pass2", valid=True
        ))

        self.database.session.commit()

    def testGetAllConnections(self):
        connections = list(self.database.getAllConnections())
        self.assertEqual(2, len(connections))
        self.assertEqual("aaasdsd.asd.de", connections[0].host)
        self.assertEqual("user1", connections[0].username)
        self.assertEqual("pass1", connections[0].password)
        self.assertEqual(False, connections[0].valid)
        self.assertEqual("aaasdsd.asd.de", connections[1].host)
        self.assertEqual("user2", connections[1].username)
        self.assertEqual("pass2", connections[1].password)
        self.assertEqual(True, connections[1].valid)

    def testFindActiveConnections(self):
        connections = list(self.database.findValidConnections())
        self.assertEqual(1, len(connections))
        self.assertEqual("user2", connections[0].username)

    def testMakeConnectionInvalid(self):
        connections = list(self.database.findValidConnections())
        myValid = connections[0]
        myValid.valid = False
        self.database.session.add(myValid)

        connections = list(self.database.findValidConnections())
        self.assertNotIn(myValid, connections)
        self.database.session.rollback()


if __name__ == '__main__':
    unittest.main()
