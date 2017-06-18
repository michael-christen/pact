from schematics.models import Model
from schematics import types

from .diff import diff_hash_with_rules


class BaseModel(Model):
    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)
        self.validate()


class DiffModel(BaseModel):
    def __init__(self, obj, context=None):
        super(DiffModel, self).__init__(obj, context=context)
        self._content = obj

    def diff(self, actual):
        raise NotImplementedError("Implement in subclass")


class Request(DiffModel):
    body = types.BaseType()
    headers = types.BaseType()
    path = types.BaseType()
    method = types.BaseType()
    query = types.BaseType()

    def __init__(self, obj, context=None):
        # TODO: Move to type
        obj['method'] = obj.get('method', '').lower()
        super(Request, self).__init__(obj, context=context)

    def diff(self, actual):
        assert isinstance(actual, Request)
        return diff_hash_with_rules(
            self._content, actual._content,
            {
                'headers': dict(
                    allow_unexpected_keys=True,
                    ignore_value_whitespace=True,
                    case_insensitive_keys=True),
            })


class Response(DiffModel):
    body = types.BaseType()
    headers = types.BaseType()
    status = types.BaseType()

    def diff(self, actual):
        assert isinstance(actual, Response)
        return diff_hash_with_rules(
            self._content, actual._content,
            {
                'body': dict(
                    allow_unexpected_keys=True),
                'headers': dict(
                    allow_unexpected_keys=True,
                    ignore_value_whitespace=True,
                    case_insensitive_keys=True),
            })


class Interaction(BaseModel):
    description = types.StringType(required=True)
    providerState = types.StringType(required=True)
    request = types.ModelType(Request, required=True)
    response = types.ModelType(Response, required=True)


class NamedModel(BaseModel):
    name = types.StringType(required=True)


class Consumer(NamedModel):
    pass


class Provider(NamedModel):
    pass


class PactSpecification(BaseModel):
    version = types.StringType(required=True)


class Metadata(BaseModel):
    pactSpecification = types.ModelType(PactSpecification, required=True)


class Pact(BaseModel):
    consumer = types.ModelType(Consumer, required=True)
    provider = types.ModelType(Provider, required=True)
    interactions = types.ListType(types.ModelType(Interaction), min_size=1)
    metadata = types.ModelType(Metadata, required=True)
