# import requests
# import requests_mock

from unittest import TestCase

from .utils import get_all_json_specs


# class StubClient(object):
#     def get_value(self):
#         return requests.get('http://google.com').text
#
#
# class TestBasic(TestCase):
#     def setUp(self):
#         self.client = StubClient()
#
#     def test_mock_request(self):
#         with requests_mock.mock() as m:
#             m.get('http://google.com', text='data')
#             self.assertEqual(self.client.get_value(), 'data')


class TestSpec1(TestCase):
    def setUp(self):
        self.specs = get_all_json_specs()

    def test_each(self):
        for spec in self.specs:
            print unicode(spec)
            print ''

        self.fail('shucks')
