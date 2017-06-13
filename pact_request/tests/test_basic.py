from parameterized import parameterized
from unittest import TestCase

from .utils import get_all_json_specs
from ..diff import PactDiffFormatter


class TestSpecVersion1(TestCase):
    @parameterized.expand([
        (spec.test_string(), spec.content)
        for spec in get_all_json_specs(version='1')])
    def test_pact_spec(self, name, spec_content):
        # print unicode(spec_content)
        diffs = spec_content.expected.diff(spec_content.actual)
        if spec_content.match:
            self.assertEqual(len(diffs), 0)
        else:
            self.assertGreater(len(diffs), 0)
        if diffs:
            formatted_diff = PactDiffFormatter().format_diffs(diffs)
            print formatted_diff
