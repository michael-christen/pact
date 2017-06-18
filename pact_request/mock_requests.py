from functools import wraps
from httmock import all_requests
from httmock import HTTMock
from httmock import response

from .models import Request
from .diff import PactDiffFormatter


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
    def __init__(self, interactions=None):
        # TODO: add provider, consumer spec
        super(MockRequests, self).__init__()
        self.htt_mock = HTTMock(self.response_content)
        self.interactions = interactions or []

    @all_requests
    def response_content(self, url, request):
        # TODO: path ending has / appended to it
        match = None
        for interaction in self.interactions:
            """Return response if request matches web_request."""
            # TODO: query
            # TODO: Figure out wtf is going on here
            diff = interaction.request._content.diff(Request(dict(
                headers=request.headers,
                body=request.body,
                path=request.url,
                method=request.method)))
            if not diff:
                match = interaction.response
                break
            else:
                # TODO: better debugging
                print PactDiffFormatter().format_diffs(diff)
        if match:
            return response(
                status_code=match.status,
                content=match.body,
                headers=match.headers,
            )
        else:
            # Not found
            return {'status_code': 404}

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
