import urllib2


class Difference(object):
    def __init__(self, expected, actual):
        # Ensure there actually is a difference
        assert expected != actual
        self.expected = expected
        self.actual = actual

    def __unicode__(self):
        return u'Expected {expected}, but got {actual}'.format(
            self.expected, self.actual)


# Singleton
ABSENT = object()


class UnexpectedActual(Difference):
    def __init__(self, actual):
        super(UnexpectedActual, self).__init__(ABSENT, actual)


class ActualNotFound(Difference):
    def __init__(self, expected):
        super(ActualNotFound, self).__init__(expected, ABSENT)


# Actual differences used
class UnexpectedIndex(UnexpectedActual):
    pass


class UnexpectedKey(UnexpectedActual):
    pass


class IndexNotFound(ActualNotFound):
    pass


class KeyNotFound(ActualNotFound):
    pass


def diff_hash_with_rules(expected, actual, key_rules):
    assert isinstance(expected, dict)
    assert isinstance(actual, dict)
    diff_tree = {}
    received_diff = False
    for expected_k, expected_v in expected.iteritems():
        rules = key_rules.get(expected_k, {})
        diff_engine = PactDiffEngine(**rules)
        actual_v = actual[expected_k]
        diff_tree[expected_k] = diff_engine.diff_val(expected_v, actual_v)
        if diff_engine.diff_received:
            received_diff = True
    if received_diff:
        print diff_tree
        return diff_tree
    else:
        return {}


class PactDiffEngine(object):
    def __init__(self,
                 allow_unexpected_keys=False,
                 ignore_value_whitespace=False,
                 case_insensitive_keys=False):
        self.allow_unexpected_keys = allow_unexpected_keys
        self.ignore_value_whitespace = ignore_value_whitespace
        self.case_insensitive_keys = case_insensitive_keys
        # Keep track of whether a diff exists
        self.diff_received = False

    def diff_val(self, expected, actual):
        if type(expected) != type(actual):
            self.diff_received = True
            return Difference(expected, actual)
        # Input cleaning
        if isinstance(expected, basestring):
            if self.ignore_value_whitespace:
                expected = expected.replace(' ', '')
                actual = actual.replace(' ', '')
            expected = urllib2.urlparse.unquote(expected)
            actual = urllib2.urlparse.unquote(actual)
        # Perform diffs
        if isinstance(expected, dict):
            return self.diff_hash(expected, actual)
        elif isinstance(expected, (list, tuple)):
            return self.diff_list(expected, actual)
        elif expected != actual:
            self.diff_received = True
            return Difference(expected, actual)
        else:
            return expected

    def diff_list(self, expected, actual):
        diffs = []
        for i, expected_v in enumerate(expected):
            try:
                actual_v = actual[i]
            except IndexError:
                self.diff_received = True
                diffs.append(IndexNotFound(expected_v))
            else:
                diffs.append(self.diff_val(expected_v, actual_v))
        if len(actual) > len(expected):
            for actual_v in actual[len(expected):]:
                self.diff_received = True
                diffs.append(UnexpectedIndex(actual_v))
        return diffs

    def diff_hash(self, expected, actual):
        assert isinstance(expected, dict)
        assert isinstance(actual, dict)
        # Remove None values
        if self.allow_unexpected_keys:
            actual = {k: v for k, v in actual.iteritems() if v is not None}
        # Clean input
        if self.case_insensitive_keys:
            actual = {k.lower(): v for k, v in actual.iteritems()}
            expected = {k.lower(): v for k, v in expected.iteritems()}
        diffs = {}
        for expected_k, expected_v in expected.iteritems():
            try:
                actual_v = actual[expected_k]
            except KeyError:
                self.diff_received = True
                diffs[expected_k] = KeyNotFound(expected_v)
            else:
                diffs[expected_k] = self.diff_val(expected_v, actual_v)
        for actual_k, actual_v in actual.iteritems():
            if actual_k not in expected and not self.allow_unexpected_keys:
                self.diff_received = True
                diffs[actual_k] = UnexpectedKey(actual_v)
        return diffs
