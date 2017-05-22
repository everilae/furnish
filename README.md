# furnish
Create HTTP API clients from Python.

```python
from furnish import furnish, get, Path, Query


@furnish
class Api:

    @get("/")
    def all() -> List[Item]: pass

    @get("/{id}")
    def item(id: Path(int)) -> Item: pass

    @get("/search")
    def search(q: Query(str)) -> List[Item]: pass

api = Api("https://example.org")
# Fetch all
api.all()
# Fetch by id
api.item(1)
# Search
api.search("my query string")
```
