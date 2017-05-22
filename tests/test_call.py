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
def api_class():
    return furnish()(Api)


class TestCall:

    def test_get(self, api_class, client):
        api = api_class("http://example.org", client=client)

        api.all()
        client.assert_called_with("get", "http://example.org/")

        api.item(1)
        client.assert_called_with("get", "http://example.org/1")

        ret = api.search("foo")
        client.assert_called_with("get", "http://example.org/search",
                                  params={ "q": "foo" })
        assert ret is client.return_value
