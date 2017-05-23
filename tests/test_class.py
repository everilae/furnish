import pytest
from furnish import furnish


@pytest.fixture
def api_class():
    @furnish()
    class Api:
        pass

    return Api


class TestClass:

    def test_custom_client(self, api_class):
        client = object()
        api = api_class("", client=client)
        assert api.client is client,\
            "'furnish' allows passing custom client"

    def test_base_url(self, api_class):
        api = api_class("https://example.org")
        assert api.base_url == "https://example.org"
