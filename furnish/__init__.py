import inspect
import requests
from functools import partial, partialmethod, update_wrapper
from collections import namedtuple
from copy import copy
from typing import TypeVar, Generic, Callable, Optional, Type

Response = TypeVar("Response")


class _Signature(inspect.Signature):

    def _get_annotated(self, type_, arguments):
        v = {}
        for name, value in arguments.items():
            annotation = self.parameters[name].annotation
            if isinstance(annotation, type_):
                v[annotation.name or name] = value

        return v

    def path_vars(self, arguments):
        return self._get_annotated(Path, arguments)

    def query_params(self, arguments):
        return self._get_annotated(Query, arguments)

    def body(self, arguments):
        return None


class BaseClient:
    """
    Base client class.
    """

    _client = None

    def _call(self,
              method: str,
              template: str,
              signature: _Signature,
              *args, **kwgs) -> Response:
        """
        Send an HTTP request using `_client`.
        """
        bound = signature.bind(*args, **kwgs)
        bound.apply_defaults()

        url = template.format(**signature.path_vars(bound.arguments))
        kwgs = {}

        query_params = signature.query_params(bound.arguments)
        if query_params:
            kwgs["params"] = query_params

        body = signature.body(bound.arguments)
        if body:
            kwgs["data"] = body

        self._client(method, url, **kwgs)


def _isfurnished(member):
    return inspect.isfunction(member) and hasattr(member, "_furnish")


def furnish(cls: Optional[Type]=None, *, client=requests.request) -> Type[BaseClient]:
    """
    Create HTTP API client from class definition.
    """
    if cls is None:
        return partial(furnish, client=client)

    namespace = dict(_client=client)
    for name, member in inspect.getmembers(cls, _isfurnished):
        method, template = member._furnish
        signature = _Signature.from_callable(member)
        namespace[name] = partialmethod(
            BaseClient._call, method, template, signature)

    return type(cls.__name__, (BaseClient,), namespace)


def url(method: str, template: str) -> Callable[[Callable], Callable]:
    """
    Define URL template.
    """
    def decorator(f: Callable) -> Callable:
        f._furnish = (method, template)
        return f

    return decorator

get = partial(url, "get")
post = partial(url, "post")
put = partial(url, "put")
patch = partial(url, "patch")
delete = partial(url, "delete")
head = partial(url, "head")


class Parameter:
    """
    Parameter annotation.
    """

    def __init__(self, type_: Type, name: Optional[str]=None) -> None:
        self.type_ = type_
        self.name = name


class Path(Parameter):
    """
    Path parameter.
    """


class Query(Parameter):
    """
    Query parameter.
    """
