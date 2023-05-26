# madtypes
- 💢 Python class typing that will tell you to <censored> at runtime
- 📖 Render to dict or json
- 🌐 [Json-Schema](https://json-schema.org/)

### Example

```python
from madtypes import Schema

class Item(Schema)
    name: str

e = Item()

e.name = 2 # will raise ValueError

```
  
### json-schema
  
```python
from madtypes import schema, Schema

class Item(Schema):
    name: str

class Basket(Schema):
    items: list[Item]

assert schema(Basket) == {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
            },
        }
    },
}
```

### Installation

```bash
pip3 install madtypes
```
