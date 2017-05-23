import pytest
from unittest import mock
from furnish import furnish, get, post, Path, Query, Body, Response
from typing import List


class Item:

    def __init__(self, foo, bar):
        self.foo = foo
        self.bar = bar


class Api:

    @get("/")
    def all() -> List[Item]: pass

    @get("/{id}")
    def item(id: Path(int)) -> Item: pass

    @post("/")
    def create_item(item: Body(dict)) -> None: pass

    @get("/search")
    def search(q: Query(str)) -> List[Item]: pass


@pytest.fixture(scope="function")
def client():
    return mock.Mock()


@pytest.fixture
def api_class():
    return furnish(Api)


class TestCall:

    def test_get(self, api_class, client):
        api = api_class("http://example.org", client=client)

        api.all()
        client.assert_called_with("get", "http://example.org/")

        api.item(1)
        client.assert_called_with("get", "http://example.org/1")

        api.create_item({ "name": "Test" })
        client.assert_called_with("post", "http://example.org/",
                                  data={ "name": "Test" })

        ret = api.search("foo")
        client.assert_called_with("get", "http://example.org/search",
                                  params={ "q": "foo" })
        assert ret.response is client.return_value

    def test_body(self, api_class, client):
        api = api_class("http://example.org", client=client)

        the_json = { "foo": 1, "bar": 2 }
        mock_response = mock.Mock()
        mock_response.json.return_value = the_json
        client.return_value = mock_response

        response = api.item(1)
        assert isinstance(response, Response)
        assert response.json() == the_json

        item = response.body()
        assert isinstance(item, Item)
        assert item.foo == 1 and item.bar == 2
