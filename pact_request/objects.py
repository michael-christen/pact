from .diff import PactDiffEngine
from .diff import PactHeaderDiffEngine


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
