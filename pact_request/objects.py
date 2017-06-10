from itertools import izip_longest
import urllib2

unquote = urllib2.urlparse.unquote



class Difference(object):
    def __init__(self, expected, actual):
        # Ensure there actually is a difference
        assert expected != actual
        self.expected = expected
        self.actual = actual

    def __unicode__(self):
        return u'Expected {expected}, but got {actual}'.format(
            self.expected, self.actual)


def diff_headers(expected, actual, allow_unexpected_keys=False):
    # Case insensitive, remove whitespace
    expected = {k.lower(): v.replace(' ', '') for k,v in expected.iteritems()}
    actual = {k.lower(): v.replace(' ', '') for k,v in actual.iteritems()}
    diffs = []
    for expected_k, expected_v in expected.iteritems():
        try:
            actual_v = actual[expected_k]
        except KeyError as e:
            diffs.append(e)
        else:
            if expected_v != actual_v:
                diffs.append('{} != {}'.format(actual_v, expected_v))
    if not allow_unexpected_keys and (
            set(expected.keys()) != set(actual.keys())):
        diffs.append("unexpected keys")
    return diffs


def diff_val(expected, actual, allow_unexpected_keys):
    if type(expected) != type(actual):
        return ['{} mismatch type {}'.format(expected, actual)]
    if isinstance(expected, dict):
        return diff_hash(expected, actual, allow_unexpected_keys)
    elif isinstance(expected, (list, tuple)):
        return diff_list(expected, actual, allow_unexpected_keys)
    elif expected != actual:
        return ['{} not equal {}'.format(expected, actual)]
    else:
        return []


def diff_list(expected, actual, allow_unexpected_keys):
    diffs = []
    for expected_v, actual_v in izip_longest(expected, actual):
        diffs.extend(diff_val(expected_v, actual_v, allow_unexpected_keys))
    return diffs


def diff_hash(expected, actual, allow_unexpected_keys=False):
    assert isinstance(expected, dict)
    assert isinstance(actual, dict)
    # Remove None values
    actual = {k:v for k,v in actual.iteritems() if v is not None}
    diffs = []
    if not allow_unexpected_keys and (
            set(expected.keys()) != actual.keys()):
        diffs.append("unexpected keys")
    for expected_k, expected_v in expected.iteritems():
        try:
            actual_v = actual[expected_k]
        except KeyError:
            diffs.append("Key not found <{}>".format(expected_k))
        else:
            diffs.extend(diff_val(expected_v, actual_v, allow_unexpected_keys))
    return diffs


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
        if self.status is None:
            if actual.status is not None:
                diffs.append("Actual not None")
        else:
            try:
                if int(self.status) != int(actual.status):
                    diffs.append('status')
            except TypeError as e:
                # actual.status is None
                diffs.append(e)
        # .headers == name & values for expected
        header_diffs = diff_headers(
            self.headers, actual.headers, allow_unexpected_keys=True)
        if header_diffs:
            diffs.extend(header_diffs)
        # .body == allow unexpected keys, no unexpected items in array
        diffs.extend(diff_val(
            self.body, actual.body, allow_unexpected_keys=True))
        print diffs
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
        diffs = []
        # .method == (case-insensitive)
        if self.method.lower() != actual.method.lower():
            diffs.append('method !=')
        # .path == (care about trailing /)
        if self.path != actual.path:
            diffs.append('path')
        # .query ==
        if type(self.query) == type(actual.query):
            if unquote(self.query) != unquote(actual.query):
                diffs.append('query')
        else:
            diffs.append('query wrong types')
        # .headers == name & values for expected
        header_diffs = diff_headers(self.headers, actual.headers,
                allow_unexpected_keys=True)
        if header_diffs:
            diffs.extend(header_diffs)
        # .body (no unexpected keys, no unexpected items in an array)
        diffs.extend(diff_val(
            self.body, actual.body, allow_unexpected_keys=False))
        print diffs
        return diffs
