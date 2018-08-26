import requests

from typing import Optional, Type, Union, TypeVar, Generic, List, Tuple
from typing.io import IO

from .exc import FurnishError

JSON = Union[int, float, str, dict, list, bool, None]


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


class _BaseBody(Parameter):
    """
    Common base class for different request body handlers.
    """


class Body(_BaseBody):
    """
    Request body.
    """


class Json(_BaseBody):
    """
    Request body, serialized as JSON.
    """
    def __init__(self, type_: Type=JSON, name: Optional[str]=None) -> None:
        super().__init__(type_, name)


class File(_BaseBody):
    """
    Multipart request file part.
    """

    def __init__(self, name: Optional[str]=None) -> None:
        super().__init__(Union[IO, Tuple[str, IO]], name)


class Header(Parameter):
    """
    Request header.

    Note the reversed parameters to `__init__`; a header always requires
    a name, but usually will default to a `str`.
    """

    def __init__(self, name: str, type_: Type=str) -> None:
        super().__init__(type_, name)

T = TypeVar("T")


def _deserialize(cls: Type[T], json_: JSON) -> T:
    """
    Simple JSON deserializer.
    """
    if issubclass(cls, list):
        item_cls, = cls.__args__
        obj = [_deserialize(item_cls, x) for x in json_]

    else:
        obj = cls.__new__(cls)
        # TODO: Deserialize attributes
        obj.__dict__.update(json_)

    return obj


# TODO: This adapts requests.Response objects, there should exist
# a response interface that other adapters could implement.
class Response(Generic[T]):
    """
    Wraps actual HTTP client responses.
    """

    def __init__(self,
                 response: requests.Response,
                 body_cls: Optional[Type[T]]):
        self.response = response
        self.body_cls = body_cls
        self._entity = None

    def json(self, **kwgs) -> JSON:
        """
        Returns the body if any, decoded from JSON.
        """
        return self.response.json(**kwgs)

    def _check_error(self):
        try:
            self.response.raise_for_status()

        except requests.HTTPError as e:
            raise FurnishError("an HTTP error occurred") from e

    def body(self) -> T:
        """
        Returns the body deserialized from JSON as `T`.
        """
        if self.body_cls is None:
            raise FurnishError("missing type information")

        if not self._entity:
            self._check_error()
            body_json = self.response.json()
            self._entity = _deserialize(self.body_cls, body_json)

        return self._entity
