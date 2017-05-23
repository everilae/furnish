import inspect
import requests
from functools import partial, partialmethod, update_wrapper
from collections import namedtuple
from copy import copy
from typing import TypeVar, Generic, Callable, Optional, Type

from .exc import FurnishError
from .types import Path, Query, Body
from .utils import LockPick as _LockPick

Response = TypeVar("Response")


def _get_parameters(type_, signature):
    return ((name, parameter)
            for name, parameter in signature.parameters.items()
            if isinstance(parameter.annotation, type_))


def _check_signature(signature, template):
    """
    Check that the given `Signature` is valid.
    """
    pick = _LockPick()
    template.format_map(pick)
    path_vars = {name for name, _ in _get_parameters(Path, signature)}
    path_vars_diff = pick.keys - path_vars

    if path_vars_diff:
        raise FurnishError(
            "missing Path parameters: {}".format(path_vars_diff))

    if len(list(_get_parameters(Body, signature))) > 1:
        raise FurnishError("multiple parameters annotated as Body")


def _get_args(type_, signature, bound):
    v = {}
    for name, parameter in _get_parameters(type_, signature):
        value = bound.arguments[name]
        v[parameter.annotation.name or name] = value

    return v

_path = partial(_get_args, Path)
_query = partial(_get_args, Query)


def _body(signature, bound):
    args = _get_args(Body, signature, bound)

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

        url = self.baseUrl + template.format_map(_path(signature, bound))
        kwgs = {}

        query = _query(signature, bound)
        if query:
            kwgs["params"] = query

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
            base_class._call, method, template, signature)

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
