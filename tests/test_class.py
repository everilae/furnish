import pytest
from furnish import create


@pytest.fixture
def api_cls():
    class Api:
        pass

    return Api


class TestClass:

    def test_custom_client(self, api_cls):
        client = object()
        api = create(api_cls, "", client=client)
        assert api.client is client,\
            "'furnish' allows passing custom client"

    def test_base_url(self, api_cls):
        api = create(api_cls, "https://example.org")
        assert api.base_url == "https://example.org"
