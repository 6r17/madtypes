# madtypes
- 💢 Python class typing that raise TypeError at runtime
- 📖 Render to dict or json
- 🌐 [Json-Schema](https://json-schema.org/)

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
  
- ### json-schema
  
```python
from madtypes import json_schema, Schema
from typing import Optional

class Item(Schema):
    name: Optional[str]

class Basket(Schema):
    items: list[Item]

assert json_schema(Basket) == {
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

- ### 🔥 Annotation attributes
It is possible to use the `Annotation` metaclass customize a type.

```python
class SomeStringAttribute(str, metaclass=Annotation):
   pass

SomeDescriptedAttribute(2) # raise type error
```

It is possible to use this to further describe a field.

```python
class SomeDescriptedAttribute(str, metaclass=Annotation):
    annotation = str
    description = "Some description"
```

using `json_schema` on `SomeDescription` will include the description attribute

```python
class DescriptedString(str, metaclass=Annotation):
    description = "Some description"
    annotation = str

class DescriptedItem(Schema):
    descripted: DescriptedString

assert json_schema(DescriptedItem) == {
    "type": "object",
    "properties": {
        "descripted": {
            "type": "string",
            "description": "Some description",
        },
    },
    "required": ["descripted"],
}

```

- ### Regular expression

Regex can be defined on an Annotated type using the `pattern` attribute.

:warning: be careful to respect the json-schema [specifications](https://json-schema.org/understanding-json-schema/reference/regular_expressions.html) when using `json_schema`
It this moment this is not checked and will render an invalid `json-schema`.

```python

def test_pattern_definition_allows_normal_usage():
    class PhoneNumber(str, metaclass=Annotation):
        annotation = str
        pattern = r"\d{3}-\d{3}-\d{4}"

    PhoneNumber("000-000-0000")


def test_pattern_raise_type_error():
    class PhoneNumber(str, metaclass=Annotation):
        annotation = str
        pattern = r"\d{3}-\d{3}-\d{4}"

    with pytest.raises(TypeError):
        PhoneNumber("oops")


def test_pattern_is_rendered_in_json_schema():
    class PhoneNumber(str, metaclass=Annotation):
        annotation = str
        pattern = r"^\d{3}-\d{3}-\d{4}$"
        description = "A phone number in the format XXX-XXX-XXXX"

    class Contact(Schema):
        phone: PhoneNumber

    schema = json_schema(Contact)
    print(json.dumps(schema, indent=4))
    assert schema == {
        "type": "object",
        "properties": {
            "phone": {
                "pattern": "^\\d{3}-\\d{3}-\\d{4}$",
                "description": "A phone number in the format XXX-XXX-XXXX",
                "type": "string",
            }
        },
        "required": ["phone"],
    }
```

- ### Object validation

It is possible to define a `is_valid` method on a `Schema` object, which is during instantiation
to allow restrictions based on multiple fields.

```python

def test_object_validation():
    class Item(Schema):
        title: Optional[str]
        content: Optional[str]

        def is_valid(self, **kwargs):
            """title is mandatory if content is absent"""
            return (
                False
                if not kwargs.get("content", None)
                and not kwargs.get("title", None)
                else True
            )

    Item(
        title="foo"
    )  # we should be able to create with only one of title or content
    Item(content="foo")
    with pytest.raises(TypeError):
        Item()



```

- ### Immutables

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

[![Test](https://github.com/6r17/madtypes/actions/workflows/test.yaml/badge.svg)](./tests/test_schema.py)
[![pypi](https://img.shields.io/pypi/v/madtypes)](https://pypi.org/project/madtypes/)
![python: >3.9](https://img.shields.io/badge/python-%3E3.9-informational)
### Installation

```bash
pip3 install madtypes
```

- ### Context
`madtypes` is a Python3.9+ library that provides enhanced data type checking capabilities. It offers features beyond the scope of [PEP 589](https://peps.python.org/pep-0589/) and is built toward an industrial use-case that require reliability.

- The library introduces a Schema class that allows you to define classes with strict type enforcement. By inheriting from Schema, you can specify the expected data structure and enforce type correctness at runtime. If an incorrect type is assigned to an attribute, madtypes raises a TypeError.

- Schema class and it's attributes inherit from `dict`. Attributes are considered values of the dictionnary.

- It renders natively to `JSON`, facilitating data serialization and interchange.

- The library also includes a `json_schema()` function that generates JSON-Schema representations based on class definitions.
