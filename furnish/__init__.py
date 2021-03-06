import inspect
import requests
from functools import partial, partialmethod
from collections import namedtuple
from typing import Callable, Optional, Type, Mapping

from .exc import FurnishError
from .types import Path, Query, Body, Json, File, Header, Response
from .utils import LockPick as _LockPick

__version__ = '0.2.1'


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

    for type_ in [Body, Json]:
        if len(list(_get_parameters(type_, signature))) > 1:
            raise FurnishError(
                "multiple parameters annotated as {}".format(type_.__name__))


def _get_args(type_, signature, bound):
    v = {}
    for name, parameter in _get_parameters(type_, signature):
        value = bound.arguments[name]
        v[parameter.annotation.name or name] = value

    return v


def _get_arg(type_, signature, bound):
    args = _get_args(type_, signature, bound)

    if not args:
        return

    arg, = args.values()
    return arg

_path = partial(_get_args, Path)
_query = partial(_get_args, Query)
_headers = partial(_get_args, Header)
_body = partial(_get_arg, Body)
_json = partial(_get_arg, Json)
_files = partial(_get_args, File)


def _response_cls(signature):
    cls = signature.return_annotation
    if cls is inspect.Signature.empty:
        return None

    return cls


def _body_cls(response_cls):
    body_cls = None
    # Python 3.8 generics don't have __args__ unless specialized.
    args = getattr(response_cls, "__args__", None)

    if args:
        body_cls = args[0]

    return body_cls


_default_client = requests.request


class BaseClient:
    """
    Base client class.
    """

    def __init__(self,
                 base_url: str,
                 client=_default_client,
                 response_cls: Type[Response]=Response):
        self.base_url = base_url
        self.client = client
        self.response_cls = response_cls

    def _call(self,
              signature: inspect.Signature,
              method: str,
              template: str,
              headers: Optional[Mapping[str, str]],
              response_cls: Optional[Type[Response]],
              *args, **kwgs) -> Response:
        """
        Send an HTTP request using `client`.
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

        json_ = _json(signature, bound)
        if json_:
            kwgs["json"] = json_

        files = _files(signature, bound)
        if files:
            kwgs["files"] = files

        combined_headers = _headers(signature, bound)
        if headers:
            combined_headers.update(headers)

        if combined_headers:
            kwgs["headers"] = combined_headers

        response = self.client(method, url, **kwgs)

        response_cls = response_cls or self.response_cls
        body_cls = _body_cls(response_cls)
        return response_cls(response, body_cls)


def _isfurnished(member):
    return inspect.isfunction(member) and hasattr(member, "_furnish")


def create(cls: Type,
           *args,
           base_cls: Type[BaseClient]=BaseClient,
           **kwgs) -> Type[BaseClient]:
    """
    Create HTTP API client from class definition.
    """
    namespace = {}
    for name, member in inspect.getmembers(cls, _isfurnished):
        method, template, headers = member._furnish

        if method is None:
            raise FurnishError(
                "method not defined – possibly missing url decorator?")

        if template is None:
            raise FurnishError(
                "template not defined – possibly missing url decorator?")

        signature = inspect.signature(member)
        _check_signature(signature, template)

        response_cls = _response_cls(signature)
        namespace[name] = partialmethod(
            base_cls._call, signature, method, template, headers, response_cls)

    return type(cls.__name__, (base_cls,), namespace)(*args, **kwgs)


_Marker = namedtuple("Marker", "method template headers")

Decorator = Callable[[Callable], Callable]


def _mark(f, **kwgs):
    try:
        f._furnish = f._furnish._replace(**kwgs)

    except AttributeError:
        f._furnish = _Marker(*map(kwgs.get, _Marker._fields))


def url(method: str, template: str) -> Decorator:
    """
    Define URL template.
    """
    def decorator(f: Callable) -> Callable:
        _mark(f, method=method, template=template)
        return f

    return decorator

get = partial(url, "get")
post = partial(url, "post")
put = partial(url, "put")
patch = partial(url, "patch")
delete = partial(url, "delete")
head = partial(url, "head")


def headers(headers_map: Mapping[str, str]) -> Decorator:
    """
    Define request headers.
    """
    def decorator(f: Callable) -> Callable:
        _mark(f, headers=headers_map)
        return f

    return decorator
