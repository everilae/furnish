from typing import Optional
import furnish


class FakeService:

    @furnish.get("/posts")
    def all_posts(user_id: furnish.Query(Optional[int], "userId")=None): pass

    @furnish.post("/posts")
    def create_post(post: furnish.Body(dict)): pass

    @furnish.post("/posts")
    def create_post_json(post: furnish.Json()): pass

    @furnish.get("/posts/{id}")
    def get_post(id: furnish.Path(int)): pass

    @furnish.put("/posts/{id}")
    def replace_post(id: furnish.Path(int),
                     post: furnish.Body(dict)): pass

    @furnish.patch("/posts/{id}")
    def update_post(id: furnish.Path(int),
                    post: furnish.Body(dict)): pass

    @furnish.delete("/posts/{id}")
    def remove_post(id: furnish.Path(int)): pass

    @furnish.get("/comments")
    def comments(post_id: furnish.Query(int, "postId")): pass
