# madtypes
- 💢 Python class typing that will raise TypeError at runtime
- 📖 Render to dict or json
- 🌐 [Json-Schema](https://json-schema.org/)

### Example

```python
from madtypes import Schema

class Item(Schema)
    name: str

e = Item()

e.name = 2 # will raise TypeError

Item(name="foo") # ok
Item(name=2) # will raise TypeError

repr(Item(name="foo")) == {"name": "foo"}

json.dumps(Item(name="foo")) => '{"name": "foo"}'
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

[![Test](https://github.com/6r17/madtypes/actions/workflows/test.yaml/badge.svg)](./tests/test_schema.py)
[![pypi](https://img.shields.io/pypi/v/madtypes)](https://pypi.org/project/madtypes/)
![python: >3.9](https://img.shields.io/badge/python-%3E3.9-informational)
### Installation

```bash
pip3 install madtypes
```
