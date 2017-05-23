import pytest
import furnish
from furnish import url, get, post, BaseClient, Body

from furnish.exc import FurnishError


class TestDecorators:

    def test_simple_definition(self):
        @furnish.furnish
        class Api:
            pass

        assert issubclass(Api, BaseClient),\
            "'furnish' produces 'furnish.BaseClient' subclasses"

    def test_attributes(self):
        @furnish.furnish
        class Api:
            @get("")
            def method1():
                pass

            @get("")
            def method2():
                pass

        assert hasattr(Api, 'method1') and hasattr(Api, 'method1'),\
            "'furnish' creates methods"

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

            assert f._furnish == (method, "/")

    def test_validation(self):
        with pytest.raises(FurnishError,
                           message="Multiple Body parameters raise error"):
            @furnish.furnish
            class Api:
                @post("")
                def create(body1: Body(dict), body2: Body(dict)): pass

        with pytest.raises(FurnishError,
                           message="Missing Path parameters raise error"):
            @furnish.furnish
            class Api:
                @get("/{network}/item/{id}/")
                def get():
                    pass
