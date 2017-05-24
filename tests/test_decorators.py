import pytest
import furnish
from furnish import create, url, get, post, headers, BaseClient, Body

from furnish.exc import FurnishError


@pytest.fixture
def test_headers():
    return {
        "X-Test": "test"
    }


class TestDecorators:

    def test_simple_definition(self):
        class Api:
            pass

        api = create(Api, "")
        assert isinstance(api, BaseClient),\
            "'create' produces 'furnish.BaseClient' instances"

    def test_attributes(self):
        class Api:
            @get("")
            def method1():
                pass

            @get("")
            def method2():
                pass

        api = create(Api, "")
        assert hasattr(api, 'method1') and hasattr(api, 'method1'),\
            "furnish creates methods"

    def test_url(self):
        @url("get", "/items/{id}")
        def fun():
            pass

        assert hasattr(fun, "_furnish"),\
            "'url' decorator sets '_furnish' attribute"

    def test_http_methods(self):
        methods = ["get", "post", "put", "patch", "delete", "head"]
        for method in methods:
            deco = getattr(furnish, method)
            @deco("/")
            def f():
                pass

            assert f._furnish.method == method
            assert f._furnish.template == "/"

    def test_validation(self):
        with pytest.raises(FurnishError,
                           message="Multiple Body parameters raise error"):
            class Api:
                @post("")
                def create(body1: Body(dict), body2: Body(dict)): pass

            create(Api, "")

        with pytest.raises(FurnishError,
                           message="Missing Path parameters raise error"):
            class Api:
                @get("/{network}/item/{id}/")
                def get():
                    pass

            create(Api, "")

    def test_headers(self, test_headers):
        @headers(test_headers)
        def fun():
            pass

        assert hasattr(fun, "_furnish")
        assert fun._furnish.headers == test_headers

    def test_url_and_headers(self, test_headers):
        @headers(test_headers)
        @url("get", "/")
        def fun():
            pass

        assert hasattr(fun, "_furnish")
        assert fun._furnish.method == "get"
        assert fun._furnish.template == "/"
        assert fun._furnish.headers == test_headers
