import pytest
from unittest import mock
from furnish import furnish, get, Path, Query


class Api:

    @get("/")
    def all(): pass

    @get("/{id}")
    def item(id: Path(int)): pass

    @get("/search")
    def search(q: Query(str)): pass


@pytest.fixture
def client():
    return mock.Mock()


@pytest.fixture
def api_class(client):
    return furnish(client=client)(Api)


class TestCall:

    def test_get(self, api_class, client):
        assert api_class._client is client
        api = api_class()

        api.all()
        client.assert_called_with("get", "/")

        api.item(1)
        client.assert_called_with("get", "/1")

        api.search("foo")
        client.assert_called_with("get", "/search", params={ "q": "foo" })
