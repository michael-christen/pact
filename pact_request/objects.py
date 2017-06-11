from .diff import diff_hash_with_rules


class PactResponse(object):
    def __init__(self, dictionary):
        for key in dictionary.keys():
            assert key in {'body', 'headers', 'status'}
        self.content = dictionary

    def __unicode__(self):
        return unicode(self.content)

    def diff(self, actual):
        assert isinstance(actual, PactResponse)
        return diff_hash_with_rules(
            self.content, actual.content,
            {
                'body': dict(
                    allow_unexpected_keys=True),
                'headers': dict(
                    allow_unexpected_keys=True,
                    ignore_value_whitespace=True,
                    case_insensitive_keys=True),
            })


class PactRequest(object):
    def __init__(self, dictionary):
        for key in dictionary.keys():
            assert key in {'headers', 'path', 'body', 'method', 'query'}
        dictionary['method'] = dictionary.get('method', '').lower()
        self.content = dictionary

    def __unicode__(self):
        return unicode(self.content)

    def diff(self, actual):
        assert isinstance(actual, PactRequest)
        return diff_hash_with_rules(
            self.content, actual.content,
            {
                'headers': dict(
                    allow_unexpected_keys=True,
                    ignore_value_whitespace=True,
                    case_insensitive_keys=True),
            })
