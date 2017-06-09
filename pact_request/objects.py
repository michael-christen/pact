class Difference(object):
    def __init__(self, expected, actual):
        # Ensure there actually is a difference
        assert expected != actual
        self.expected = expected
        self.actual = actual

    def __unicode__(self):
        return u'Expected {expected}, but got {actual}'.format(
            self.expected, self.actual)


def diff_headers(expected, actual):
    diffs = []
    for expected_k, expected_v in expected.iteritems():
        try:
            actual_v = actual[expected_k]
        except KeyError as e:
            diffs.append(e)
        else:
            if expected_v != actual_v:
                diffs.append('{} != {}'.format(actual_v, expected_v))
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
        header_diffs = diff_headers(self.headers, actual.headers)
        if header_diffs:
            diffs.extend(header_diffs)
        # .body == allow unexpected keys, no unexpected items in array
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
        if self.query != actual.query:
            diffs.append('query')
        # .headers == name & values for expected
        header_diffs = diff_headers(self.headers, actual.headers)
        if header_diffs:
            diffs.extend(header_diffs)
        # .body (no unexpected keys, no unexpected items in an array)
        return diffs
