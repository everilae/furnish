import inspect
import requests
from functools import partial, partialmethod
from typing import Callable, Optional, Type

from .exc import FurnishError
from .types import Path, Query, Body, Response
from .utils import LockPick as _LockPick


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


def _body_class(signature):
    return signature.return_annotation

_default_client = requests.request


class BaseClient:
    """
    Base client class.
    """

    def __init__(self, base_url, client=_default_client):
        self.base_url = base_url
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

        url = self.base_url + template.format_map(_path(signature, bound))
        kwgs = {}

        query = _query(signature, bound)
        if query:
            kwgs["params"] = query

        body = _body(signature, bound)
        if body:
            kwgs["data"] = body

        body_class = _body_class(signature)

        response = self.client(method, url, **kwgs)
        return Response(response, body_class)


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
