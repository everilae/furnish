from furnish import furnish, url, get, BaseClient


class TestDecorators:

    def test_simple_definition(self):
        @furnish
        class Api:
            pass

        assert issubclass(Api, BaseClient),\
            "'furnish' produces 'furnish.BaseClient' subclasses"

    def test_attributes(self):
        @furnish
        class Api:
            @get("")
            def method1():
                pass

            @get("")
            def method2():
                pass

        assert hasattr(Api, 'method1') and hasattr(Api, 'method1'),\
            "'furnish' creates methods"

    def test_custom_client(self):
        client = object()

        @furnish(client=client)
        class Api:
            pass

        assert Api._client is client,\
            "'furnish' allows passing custom client"

    def test_url(self):
        @url("get", "/items/{id}")
        def fun():
            pass

        assert hasattr(fun, "_furnish"),\
            "'url' decorator sets '_furnish' attribute"
