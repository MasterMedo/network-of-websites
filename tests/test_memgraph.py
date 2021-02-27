from tests import BaseTestCase, del_mock_data
from main import (exists,
                  get_depth,
                  get_links,
                  create_url,
                  create_link,
                  get_path)


class TestMemgraph(BaseTestCase):
    def test_mocks_inserted(self):
        with self.driver.session() as session:
            self.assertTrue(session.read_transaction(exists, self.mock_start)
                                   .single())
            self.assertTrue(session.read_transaction(exists, self.mock_end)
                                   .single())
            self.assertTrue(session.read_transaction(exists, self.url1)
                                   .single())
            self.assertTrue(session.read_transaction(exists, self.url2)
                                   .single())

    def test_create_url(self):
        with self.driver.session() as session:
            session.write_transaction(create_url, self.mock_start, 4)
            depth = session.read_transaction(get_depth, self.mock_start)\
                           .single().get('depth')
            self.assertTrue(depth == 4)

    def test_create_link(self):
        with self.driver.session() as session:
            session.write_transaction(del_mock_data)
            session.write_transaction(create_url, self.mock_start, 2)
            session.write_transaction(create_link,
                                      self.mock_start,
                                      self.mock_end, 2)
            self.assertTrue(session.read_transaction(exists, self.mock_end)
                                   .single())

    def test_get_links(self):
        with self.driver.session() as session:
            links = session.read_transaction(get_links, self.mock_start)
            self.assertTrue(len(list(links)) == 3)

    def test_get_path(self):
        with self.driver.session() as session:
            path = session.read_transaction(get_path,
                                            self.mock_start,
                                            self.mock_end).single().get('path')
            self.assertTrue(len(list(path)) == 2)

    def test_empty_path(self):
        with self.driver.session() as session:
            path = session.read_transaction(get_path,
                                            self.mock_end,
                                            self.mock_start)
            self.assertTrue(path.peek() is None)
