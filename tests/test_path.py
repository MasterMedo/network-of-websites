from tests import BaseTestCase
from main import path
from exceptions import WebsiteNotFoundError, ShortestPathNotFoundError


class TestPath(BaseTestCase):
    def test_invalid_start_website(self):
        with self.assertRaises(WebsiteNotFoundError):
            path('unknown', self.mock_end, self.driver)

    def test_invalid_end_website(self):
        with self.assertRaises(WebsiteNotFoundError):
            path(self.mock_start, 'unknown', self.driver)

    def test_no_link_website(self):
        with self.assertRaises(ShortestPathNotFoundError):
            path(self.mock_end, self.mock_start, self.driver)

    def test_mock_path(self):
        path(self.mock_start, self.mock_end, self.driver)
