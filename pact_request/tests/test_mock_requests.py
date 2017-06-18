from unittest import TestCase

import requests

from ..mock_requests import MockRequests
from ..models import Interaction


class TestRequests(TestCase):
    def test_basic(self):
        # Use interaction for now
        # TODO: add convenience function
        with MockRequests([
                Interaction(dict(
                    description='Testing basic',
                    providerState='Nothing setup',
                    request=dict(
                        path='http://fake.me/',
                        method='get',
                    ),
                    response=dict(
                        status=201,
                    ),
                )),
                ]):
            response = requests.get('http://fake.me/')
            self.assertEqual(201, response.status_code)
        with MockRequests([
                Interaction(dict(
                    description='Testing basic w/ body',
                    providerState='Nothing setup',
                    request=dict(
                        path='http://fake.me/',
                        method='get',
                    ),
                    response=dict(
                        status=200,
                        body={'hey': 'guys'}
                    ),
                )),
                ]):
            response = requests.get('http://fake.me/')
            self.assertEqual({'hey': 'guys'}, response.json())
