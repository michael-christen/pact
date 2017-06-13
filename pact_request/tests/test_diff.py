from unittest import TestCase

from ..diff import PactDiffFormatter
from ..diff import diff_hash_with_rules


class TestDiff(TestCase):
    def test_basic_equality(self):
        expected = {'a': 1, 'b': [1, 2]}
        self.assertEquals({}, diff_hash_with_rules(expected, expected, {}))

    def test_ignore_whitespace_equality(self):
        expected = {'a': 'bo b', 'b': 'ca\trl'}
        actual = {'a': 'bob', 'b': 'carl'}
        self.assertGreater(len(diff_hash_with_rules(expected, actual, {})), 0)
        self.assertEquals({}, diff_hash_with_rules(expected, actual, {
            'a': dict(ignore_value_whitespace=True),
            'b': dict(ignore_value_whitespace=True),
        }))

    def test_case_insensitive_keys(self):
        expected = {'b': {'x': 1, 'Y': {'Z': 1}}}
        actual = {'b': {'X': 1, 'Y': {'z': 1}}}
        self.assertGreater(len(diff_hash_with_rules(expected, actual, {})), 0)
        self.assertEquals({}, diff_hash_with_rules(expected, actual, {
            'b': dict(case_insensitive_keys=True),
        }))

    def test_allow_unexpected_keys(self):
        expected = {'b': {'x': 1, 'y': {'z': 1}}}
        actual = {'b': {'x': 1, 'bob': 1, 'y': {'z': 1, 'a': 5}}}
        self.assertGreater(len(diff_hash_with_rules(expected, actual, {})), 0)
        self.assertEquals({}, diff_hash_with_rules(expected, actual, {
            'b': dict(allow_unexpected_keys=True),
        }))


class TestDiffFormatter(TestCase):
    def test_basic_format(self):
        expected = {'a': 'b'}
        actual = {'a': 'c'}
        diffs = diff_hash_with_rules(expected, actual, {})
        formatter = PactDiffFormatter()
        result = formatter.format_diffs(diffs)
        expected = """  {
-     "a": "b"
?           ^
+     "a": "c"
?           ^
  }"""
        self.assertEqual(expected, result)
