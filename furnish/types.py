import requests
from typing import Optional, Type, Union, TypeVar, Generic, List


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

JSON = Union[dict, list]
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
# a generic base response that other adapters implement.
class Response(Generic[T]):
    """
    Wraps actual HTTP client responses.
    """

    def __init__(self,
                 response: requests.Response,
                 body_class: Type[T]):
        self.response = response
        self.body_class = body_class
        self._entity = None

    def json(self, **kwgs) -> JSON:
        """
        Returns the body if any, decoded from JSON.
        """
        return self.response.json(**kwgs)

    def body(self) -> T:
        """
        Returns the body deserialized from JSON as `T`.
        """
        if self.body_class is None:
            raise FurnishError("missing type information")

        if not self._entity:
            body_json = self.response.json()
            self._entity = _deserialize(self.body_class, body_json)

        return self._entity
