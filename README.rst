furnish
=======

Create HTTP API clients from Python. Inspired by Retrofit_.

.. code:: python

    >>> import furnish

    >>> class FakeService:
    ... 
    ...     @furnish.get("/posts")
    ...     def all_posts(user_id: furnish.Query(Optional[int], "userId")=None): pass
    ... 
    ...     @furnish.post("/posts")
    ...     def create_post(post: furnish.Body(dict)): pass
    ... 
    ...     @furnish.get("/posts/{id}")
    ...     def get_post(id: furnish.Path(int)): pass
    ... 
    ...     @furnish.put("/posts/{id}")
    ...     def replace_post(id: furnish.Path(int),
    ...                      post: furnish.Body(dict)): pass
    ... 
    ...     @furnish.patch("/posts/{id}")
    ...     def update_post(id: furnish.Path(int),
    ...                     post: furnish.Body(dict)): pass
    ... 
    ...     @furnish.delete("/posts/{id}")
    ...     def remove_post(id: furnish.Path(int)): pass
    ... 
    ...     @furnish.get("/comments")
    ...     def comments(post_id: furnish.Query(int, "postId")): pass
    ...

    >>> service = furnish.create(FakeService, "https://jsonplaceholder.typicode.com")

    >>> service.all_posts(user_id=2).json()
    [{'userId': 2,
      'body': 'delectus reiciendis molestiae occaecati non minima eveniet qui voluptatibus\naccusamus in eum beatae sit\nvel qui neque voluptates ut commodi qui incidunt\nut animi commodi',
      'title': 'et ea vero quia laudantium autem',
      'id': 11},
      ...

    >>> service.update_post(1, { 'title': 'New title' }).json()
    {'title': 'New title',
     'id': 1,
     'userId': 1,
     'body': 'quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto'}

Supports simple deserialization of response bodies to Python objects:

.. code:: python

    >>> import furnish

    >>> class Post:
    ...     def __item__(self, *, id, title, body, userId):
    ...         self.id = id
    ...         self.title = title
    ...         self.body = body
    ...         self.userId = userId
    ... 

    >>> class FakeService:
    ...     @furnish.get("/posts/{id}")
    ...     def get_post(id: furnish.Path(int)) -> furnish.Response[Post]: pass
    ... 

    >>> service = furnish.create(FakeService, "https://jsonplaceholder.typicode.com")

    >>> service.get_post(1).body()
    <__main__.Post object at 0x7f01ef00b208>

    >>> _.title
    'sunt aut facere repellat provident occaecati excepturi optio reprehenderit'

TODO
----

-  Serialize according to annotations

License
-------

This package is licensed under the OSI MIT License.

.. _Retrofit: http://square.github.io/retrofit/
