from unittest import TestCase

import requests

from ..mock_requests import MockRequests


class TestRequests(TestCase):
    def test_basic(self):
        with MockRequests():
            response = requests.get('http://fake_website.me/')
            print response
        self.fail('hey')
