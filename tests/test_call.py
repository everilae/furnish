import pytest
from unittest import mock

from furnish import (
    create, get, post, headers, Path, Query, Body, Json, File, Header,
    Response, FurnishError)

from typing import List

import requests


class Item:

    def __init__(self, foo, bar):
        self.foo = foo
        self.bar = bar


@pytest.fixture(scope="function")
def client():
    return mock.Mock()


@pytest.fixture
def test_headers():
    return {
        "X-Secret": "super secret"
    }


@pytest.fixture
def api_cls(test_headers):
    class Api:

        @get("/")
        def all() -> Response[List[Item]]: pass

        @get("/{id}")
        def item(id: Path(int)) -> Response[Item]: pass

        @post("/")
        def create_item(item: Body(dict)) -> Response: pass

        @post("/")
        def create_item_json(item: Json()) -> Response: pass

        @get("/search")
        def search(q: Query(str)) -> Response[List[Item]]: pass

        @headers(test_headers)
        @get("/secret")
        def secret() -> Response: pass

        @get("/super_secret")
        def super_secret(auth: Header("Authorization")): pass

        @headers(test_headers)
        @get("/combo")
        def combo(auth: Header("Authorization")): pass

        @post("/file")
        def add_file(the_file: File()): pass

    return Api


@pytest.fixture(scope="function")
def api(api_cls, client):
    return create(api_cls, "http://example.org", client=client)


class TestCall:

    def test_get(self, api, client):
        api.all()
        client.assert_called_with("get", "http://example.org/")

        api.item(1)
        client.assert_called_with("get", "http://example.org/1")

        ret = api.search("foo")
        client.assert_called_with("get", "http://example.org/search",
                                  params={ "q": "foo" })
        assert ret.response is client.return_value

    def test_post(self, api, client):
        api.create_item({ "name": "Test" })
        client.assert_called_with("post", "http://example.org/",
                                  data={ "name": "Test" })

    def test_post_json(self, api, client):
        api.create_item_json({ "name": "Test" })
        client.assert_called_with("post", "http://example.org/",
                                  json={ "name": "Test" })

    def test_post_file(self, api, client):
        mock_file = mock.Mock()
        api.add_file(mock_file)
        client.assert_called_with("post", "http://example.org/file",
                                  files={ "the_file": mock_file })

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

    def test_request_headers(self, api, client, test_headers):
        api.secret()
        client.assert_called_with("get", "http://example.org/secret",
                                  headers=test_headers)

        api.super_secret("this is auth")
        client.assert_called_with("get", "http://example.org/super_secret",
                                  headers={ "Authorization": "this is auth" })

        combined_headers = { "Authorization": "this is auth" }
        combined_headers.update(test_headers)

        api.combo("this is auth")
        client.assert_called_with("get", "http://example.org/combo",
                                  headers=combined_headers)

    def test_error_response_raises(self, api, client):
        mock_response = mock.Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        client.return_value = mock_response
        response = api.item(1)
        with pytest.raises(FurnishError):
            response.body()

