# import requests
# import requests_mock

from parameterized import parameterized
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

    @parameterized.expand([
        (spec.test_string(), spec.content)
        for spec in get_all_json_specs(version='1')])
    def test_pact_spec(self, name, spec_content):
        print unicode(spec_content)
        diffs = spec_content.expected.diff(spec_content.actual)
        if spec_content.match:
            self.assertEqual(len(diffs), 0)
        else:
            self.assertGreater(len(diffs), 0)
