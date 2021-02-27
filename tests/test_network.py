from tests import BaseTestCase, del_mock_data
from main import network, get_links
from exceptions import WebsiteNotFoundError


class TestNetwork(BaseTestCase):
    def test_invalid_website(self):
        with self.assertRaises(WebsiteNotFoundError):
            network('unknown', 2, self.driver)

    def test_negative_depth(self):
        with self.assertRaises(ValueError):
            network(self.mock_start, -2, self.driver)

    def test_expanding_existing_node_with_higher_depth(self):
        with self.driver.session() as session:
            session.write_transaction(del_mock_data)

        network(self.mock_start, 0, self.driver)
        network(self.mock_start, 1, self.driver)
        with self.driver.session() as session:
            links = session.read_transaction(get_links, self.mock_start)

        self.assertTrue(all(node.get('depth') >= 1 for node in links))
