import six

from contextlib import contextmanager
from functools import wraps
from mock import patch
from httmock import all_requests
from httmock import HTTMock
from httmock import response


"""Blatant copy from responses.

TODO: Why use this vs requests.Response?
"""
try:
    from requests.packages.urllib3.response import HTTPResponse
except ImportError:
    from urllib3.response import HTTPResponse


class ContextDecorator(object):
    """Generic context manager / decorator hybrid."""
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __call__(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapped


class MockRequests(ContextDecorator):
    def __init__(self):
        super(MockRequests, self).__init__()
        self.htt_mock = HTTMock(self.response_content)

    @all_requests
    def response_content(self, url, request):
        return {'status_code': 200}

    def __enter__(self):
        self.htt_mock.__enter__()
        return super(MockRequests, self).__enter__()

    def __exit__(self, *args, **kwargs):
        self.htt_mock.__exit__(*args, **kwargs)
        return super(MockRequests, self).__exit__(*args, **kwargs)


"""
class MockRequests(ContextDecorator):
    def on_request(self, request):
        print request.__dict__
        return HTTPResponse(
            status=200,
            reason=six.moves.http_client.responses[200],
            preload_content=False)

    def __enter__(self):
        # Patch requests
        def _patched_send(adapter, request, *args, **kwargs):
            # TODO: Investigate other args
            resp = self.on_request(request)
            resp = adapter.build_response(request, resp)
            print resp.__dict__
            # Non-stream need this to check if is_fp_closed
            resp.content
            return resp

        self._patch_request = patch('requests.adapters.HTTPAdapter.send',
                                    _patched_send)
        self._patch_request.start()
        return super(MockRequests, self).__enter__()

    def __exit__(self, *args, **kwargs):
        # Remove patch of requests
        self._patch_request.stop()
        return super(MockRequests, self).__exit__(*args, **kwargs)
"""
