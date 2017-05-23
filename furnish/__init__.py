import inspect
import requests
from functools import partial, partialmethod, update_wrapper
from collections import namedtuple
from copy import copy
from typing import TypeVar, Generic, Callable, Optional, Type

Response = TypeVar("Response")


def _get_annotated(type_, signature, bound):
    v = {}
    for name, value in bound.arguments.items():
        annotation = signature.parameters[name].annotation
        if isinstance(annotation, type_):
            v[annotation.name or name] = value

    return v


def _check_signature(signature, template):
    """
    Check that the given `Signature` is valid.

    TODO: Check that required template args are present.
    """
    has_body = False
    for name, parameter in signature.parameters.items():
        annotation = parameter.annotation
        if isinstance(annotation, Body):
            if not has_body:
                has_body = True

            else:
                raise FurnishError("multiple parameters annotated as Body")


def _path_vars(signature, bound):
    return _get_annotated(Path, signature, bound)


def _query_params(signature, bound):
    return _get_annotated(Query, signature, bound)


def _body(signature, bound):
    args = _get_annotated(Body, signature, bound)

    if not args:
        return

    body, = args.values()
    return body

_default_client = requests.request


class BaseClient:
    """
    Base client class.
    """

    def __init__(self, baseUrl, client=_default_client):
        self.baseUrl = baseUrl
        self.client = client

    def _call(self,
              method: str,
              template: str,
              signature: inspect.Signature,
              *args, **kwgs) -> Response:
        """
        Send an HTTP request using `_client`.
        """
        bound = signature.bind(*args, **kwgs)
        bound.apply_defaults()

        url = self.baseUrl + template.format(**_path_vars(signature, bound))
        kwgs = {}

        query_params = _query_params(signature, bound)
        if query_params:
            kwgs["params"] = query_params

        body = _body(signature, bound)
        if body:
            kwgs["data"] = body

        return self.client(method, url, **kwgs)


def _isfurnished(member):
    return inspect.isfunction(member) and hasattr(member, "_furnish")


def furnish(cls: Optional[Type]=None, *,
            base_class: Type[BaseClient]=BaseClient) -> Type[BaseClient]:
    """
    Create HTTP API client from class definition.
    """
    if cls is None:
        return partial(furnish, base_class=base_class)

    namespace = {}
    for name, member in inspect.getmembers(cls, _isfurnished):
        method, template = member._furnish
        signature = inspect.signature(member)
        _check_signature(signature, template)
        namespace[name] = partialmethod(
            BaseClient._call, method, template, signature)

    return type(cls.__name__, (base_class,), namespace)


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


class Body(Parameter):
    """
    Request body.
    """
