import urllib2

from itertools import izip_longest


class Difference(object):
    def __init__(self, expected, actual):
        # Ensure there actually is a difference
        assert expected != actual
        self.expected = expected
        self.actual = actual

    def __unicode__(self):
        return u'Expected {expected}, but got {actual}'.format(
            self.expected, self.actual)


class PactDiffEngine(object):
    def __init__(self,
                 allow_unexpected_keys=False,
                 ignore_value_whitespace=False,
                 case_insensitive_keys=False):
        self.allow_unexpected_keys = allow_unexpected_keys
        self.ignore_value_whitespace = ignore_value_whitespace
        self.case_insensitive_keys = case_insensitive_keys

    def diff_val(self, expected, actual):
        if type(expected) != type(actual):
            return ['{} mismatch type {}'.format(expected, actual)]
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
            return ['{} not equal {}'.format(expected, actual)]
        else:
            return []

    def diff_list(self, expected, actual):
        diffs = []
        for expected_v, actual_v in izip_longest(expected, actual):
            diffs.extend(self.diff_val(expected_v, actual_v))
        if len(expected) != len(actual):
            diffs.append("None value at end of list")
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
        diffs = []
        if not self.allow_unexpected_keys and (
                set(expected.keys()) != set(actual.keys())):
            diffs.append("unexpected keys {}, {}".format(
                actual.keys(), expected.keys()))
        for expected_k, expected_v in expected.iteritems():
            try:
                actual_v = actual[expected_k]
            except KeyError:
                diffs.append("Key not found <{}>".format(expected_k))
            else:
                diffs.extend(self.diff_val(expected_v, actual_v))
        return diffs


class PactHeaderDiffEngine(PactDiffEngine):
    def __init__(self):
        super(PactHeaderDiffEngine, self).__init__(
            allow_unexpected_keys=True,
            ignore_value_whitespace=True,
            case_insensitive_keys=True)


class PactResponse(object):
    def __init__(self, dictionary):
        for key in dictionary.keys():
            assert key in {'body', 'headers', 'status'}
        self.body = dictionary.get('body', None)
        self.headers = dictionary.get('headers', {})
        self.status = dictionary.get('status', None)
        self.content = dictionary

    def __unicode__(self):
        return unicode(self.__dict__)

    def diff(self, actual):
        assert isinstance(actual, PactResponse)
        diffs = []
        # .status (integer match)
        diffs.extend(PactDiffEngine().diff_val(self.status, actual.status))
        # .body == allow unexpected keys, no unexpected items in array
        diffs.extend(PactDiffEngine(allow_unexpected_keys=True).diff_val(
            self.body, actual.body))
        # .headers == name & values for expected
        diffs.extend(PactHeaderDiffEngine().diff_hash(
            self.headers, actual.headers))
        return diffs


class PactRequest(object):
    def __init__(self, dictionary):
        for key in dictionary.keys():
            assert key in {'headers', 'path', 'body', 'method', 'query'}
        self.body = dictionary.get('body', None)
        self.headers = dictionary.get('headers', None)
        self.path = dictionary.get('path', '')
        self.method = dictionary.get('method', '')
        self.query = dictionary.get('query', '')
        self.content = dictionary

    def __unicode__(self):
        return unicode(self.__dict__)

    def diff(self, actual):
        assert isinstance(actual, PactRequest)
        basic_diff_engine = PactDiffEngine()
        # Perform diffs
        diffs = []
        diffs.extend(basic_diff_engine.diff_val(self.method.lower(),
                                                actual.method.lower()))
        diffs.extend(basic_diff_engine.diff_val(self.path, actual.path))
        diffs.extend(basic_diff_engine.diff_val(self.query, actual.query))
        diffs.extend(basic_diff_engine.diff_val(self.body, actual.body))
        # .headers == name & values for expected
        diffs.extend(PactHeaderDiffEngine().diff_hash(
            self.headers, actual.headers))
        return diffs
