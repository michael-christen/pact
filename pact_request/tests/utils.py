import glob
import os
import json


SPEC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'pact_specifications'))


class SpecResponse(object):
    def __init__(self, dictionary):
        for key in dictionary.keys():
            assert key in {'body', 'headers', 'status'}
        self.body = dictionary.get('body', None)
        self.headers = dictionary.get('headers', None)
        self.status = dictionary.get('status', None)

    def __unicode__(self):
        return unicode(self.__dict__)


class SpecRequest(object):
    def __init__(self, dictionary):
        for key in dictionary.keys():
            assert key in {'headers', 'path', 'body', 'method', 'query'}
        self.body = dictionary.get('body', None)
        self.headers = dictionary.get('headers', None)
        self.path = dictionary.get('path', None)
        self.method = dictionary.get('method', None)
        self.query = dictionary.get('query', None)

    def __unicode__(self):
        return unicode(self.__dict__)


class SpecContent(object):
    def __init__(self, dictionary, request=True):
        assumed_keys = {'comment', 'expected', 'actual', 'match'}
        assert set(dictionary.keys()) == set(assumed_keys)
        self.comment = unicode(dictionary['comment'])
        self.match = bool(dictionary['match'])
        # Dictionary of content
        if request:
            container = SpecRequest
        else:
            container = SpecResponse
        self.expected = container(dictionary['expected'])
        self.actual = container(dictionary['actual'])

    def __unicode__(self):
        match_str = '==' if self.match else "!="
        return u'Because {comment}: {actual} {match} {expected}'.format(
            comment=self.comment,
            actual=self.actual,
            match=match_str,
            expected=self.expected)


class SpecTest(object):
    def __init__(self, filename):
        file_path, basename = os.path.split(filename)
        file_path, focus = os.path.split(file_path)
        _, origin = os.path.split(file_path)
        self.origin = origin
        self.focus = focus
        self.description = os.path.splitext(basename)[0]
        with open(filename, 'r') as f:
            self.content = SpecContent(json.load(f), origin=='request')

    def __unicode__(self):
        return (
            u'Testing {description} of {focus} from {origin} with:\n{content}'
            .format(
                focus=self.focus,
                origin=self.origin,
                description=self.description,
                content=self.content))


def get_all_json_specs(version='1'):
    files = glob.glob('{}/version_{}/*/*/*.json'.format(SPEC_DIR, version))
    return [SpecTest(f) for f in files]
