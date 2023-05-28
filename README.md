# madtypes
- 💢 Python class typing that raise TypeError at runtime
- 📖 Render to dict or json
- 🌐 [Json-Schema](https://json-schema.org/)

### Example

```python
from madtypes import Schema

class Item(Schema)
    name: str

Item() # raise TypeError, name is missing
Item(name=2) # raise TypeError, 2 is not an str
Item(name="foo") # ok

repr(Item(name="foo")) == {"name": "foo"}
json.dumps(Item(name="foo")) => '{"name": "foo"}'

from typing import Optional
class ItemWithOptional(Schema):
    name: Optional[str]

ItemWithOptional() # ok
```

### Immutables

```python
from madtypes import Immutable # Immutable inherits from Schema

class Foo(Immutable):
    name: str
    age: Optional[int]

e = Foo(name="foo")

e.name = "bar" # raise TypeError


b = Foo(**e) # intianciate a new copy
b = Foo(age=2, **e) # create a copy with changes

```
  
### json-schema
  
```python
from madtypes import schema, Schema
from typing import Optional

class Item(Schema):
    name: Optional[str]

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
    "required": ["items"]
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

- Schema class and it's attributes inherit from `dict`. Attributes are considered values of the dictionnary.

- It renders natively to `JSON`, facilitating data serialization and interchange.

- The library also includes a `schema()` function that generates JSON-Schema representations based on class definitions.
