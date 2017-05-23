import requests
from typing import Optional, Type, Union, TypeVar, Generic


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

T = TypeVar("T")


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
        self._obj = None

    def json(self, **kwgs) -> Union[dict, list]:
        """
        Returns the body if any, decoded from JSON.
        """
        return self.response.json(**kwgs)

    def body(self) -> T:
        """
        Returns the body deserialized as `T`.
        """
        if not self._obj:
            body_json = self.response.json()
            self._obj = self.body_class.__new__(self.body_class)
            self._obj.__dict__.update(body_json)

        return self._obj
