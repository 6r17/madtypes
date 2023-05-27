madtypes - Enhanced Data Type Checking for Python
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

### Context
`madtypes` is a Python3.9+ library that provides enhanced data type checking capabilities. It offers features beyond the scope of [PEP 589](https://peps.python.org/pep-0589/) and is built toward an industrial use-case that require reliability.

- The library introduces a Schema class that allows you to define classes with strict type enforcement. By inheriting from Schema, you can specify the expected data structure and enforce type correctness at runtime. If an incorrect type is assigned to an attribute, madtypes raises a TypeError.

- Schema class and it's attributes inherit from `dict`. Each value is set directly in the dictionnary.

- It renders natively to `JSON`, facilitating data serialization and interchange.

- The library also includes a `schema()` function that generates JSON-Schema representations based on class definitions.

To use madtypes, install it with pip using pip3 install madtypes. The library requires Python 3.9 or later.

