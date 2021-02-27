import unittest

from neo4j import GraphDatabase
from config import uri, username, password


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = GraphDatabase.driver(uri,
                                           auth=(username, password),
                                           secure=True)
        self.mock_start = 'https://adventofcode.com/'
        self.mock_end = 'https://adventofcode.com/about'
        self.url1 = 'https://adventofcode.com/events'
        self.url2 = 'https://adventofcode.com/2020'
        self.mock_depth = 1
        with self.driver.session() as session:
            session.write_transaction(add_mock_data,
                                      self.mock_start,
                                      self.mock_end,
                                      self.url1,
                                      self.url2)

    def tearDown(self):
        with self.driver.session() as session:
            session.write_transaction(del_mock_data)

        self.driver.close()


def add_mock_data(tx, start, end, url1, url2):
    tx.run("create (a: Url {name: $start, depth: 1})"
           "create (b: Url {name: $end, depth: 0})"
           "create (c: Url {name: $url1, depth: 0})"
           "create (d: Url {name: $url2, depth: 0})"
           "create (a) - [:Links] -> (b)"
           "create (a) - [:Links] -> (c)"
           "create (a) - [:Links] -> (d)",
           start=start, end=end, url1=url1, url2=url2)


def del_mock_data(tx):
    tx.run("match (a: Url)"
           "where a.name starts with 'https://advent' "
           "detach delete a")
