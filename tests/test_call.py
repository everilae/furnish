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
    def all() -> Response[List[Item]]: pass

    @get("/{id}")
    def item(id: Path(int)) -> Response[Item]: pass

    @post("/")
    def create_item(item: Body(dict)) -> Response: pass

    @get("/search")
    def search(q: Query(str)) -> Response[List[Item]]: pass


@pytest.fixture(scope="function")
def client():
    return mock.Mock()


@pytest.fixture
def api_class():
    return furnish(Api)


@pytest.fixture(scope="function")
def api(api_class, client):
    return api_class("http://example.org", client=client)


class TestCall:

    def test_get(self, api, client):
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

    def test_body(self, api, client):
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

    def test_list_body(self, api, client):
        the_json = [
            { "foo": 1, "bar": 2 },
            { "foo": 3, "bar": 4 }
        ]
        mock_response = mock.Mock()
        mock_response.json.return_value = the_json
        client.return_value = mock_response

        response = api.all()
        assert isinstance(response, Response)
        assert response.json() == the_json

        items = response.body()
        assert isinstance(items, list)
        assert isinstance(items[0], Item)
        assert isinstance(items[1], Item)
        assert items[0].foo == 1 and items[0].bar == 2
        assert items[1].foo == 3 and items[1].bar == 4
