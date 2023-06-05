# madtypes
- 💢 `MadType` is a Python metaclass that does type-validation at run-time.
- 🌐 Generate [Json-Schema](https://json-schema.org/)
- 📖 [Type hints cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- 💪 [32 tests](https://github.com/6r17/madtypes/blob/madmeta/tests/test_integrity.py) for the features and usage of MadType class
- 💪 [18 tests](https://github.com/6r17/madtypes/blob/madmeta/tests/test_json_schema.py) for the features and usage of json-schema function

- **[PEP589](https://peps.python.org/pep-0589/) does not perform type-checking.**
> TypedDict type definitions could plausibly used to perform runtime type checking of dictionaries. For example, they could be used to validate that a JSON object conforms to the schema specified by a TypedDict type. This PEP doesn’t include such functionality, since the focus of this proposal is static type checking only, and other existing types do not support this, as discussed in Class-based syntax. Such functionality can be provided by a third-party library using the [typing_inspect](https://github.com/ilevkivskyi/typing_inspect) third-party module, for example.



```python

from typing import TypedDict
from madtypes import MadType

def test_simple_dict_incorrect_setattr(): # 🤯 DOES NOT RAISE ERROR 🤯
    class Simple(TypedDict):
        name: str

    Simple(name=2)
    a: Simple = { "name": 2 }


class Person(dict, metaclass=MadType): # 💢 MadType does !
    name: str


def test_mad_dict_type_error_with_incorrect_creation():
    with pytest.raises(TypeError):
        Person(name=2)



```


|     [![Benchmark](https://github.com/6r17/madtypes/actions/workflows/benchmark.yaml/badge.svg)](https://github.com/6r17/madtypes/actions/workflows/benchmark.yaml)               | Min   | Max   | Mean   | Min (+)        | Max (+)        | Mean (+)       |
|----------------------------:|-------|-------|--------|----------------|----------------|----------------|
| Correct instantiation      | 0.000 | 0.000 | 0.000  | 0.000 (18.1x) | 0.000 (23.8x) | 0.000 (17.3x) |
| Incorrect instantiation    | 0.000 | 0.000 | 0.000  | 0.000 (2.6x) | 0.000 (3.7x) | 0.000 (2.9x) |


- :warning: MadType instanciation is much slower than pure Python.
- :warning: Manually adding type-check inside a class is more effective than using MadType


**MadType is appropriate to apply when** :
- The described data is a business related element
- You are using MadType to assert valid data
- You are debugging
- The instantiation occurs rarely
- The schema has to be communicated with the team
 
- ### json-schema

```python

def test_object_json_schema():
    class Item(dict, metaclass=MadType):
        name: str

    assert json_schema(Item) == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }
```



- ### Further customization
It is possible to use the `MadType` metaclass customize primitives as well.

```python
class SomeStringAttribute(str, metaclass=MadType):
   pass

SomeDescriptedAttribute(2) # raise type error
```

- ### Field description

It is possible to use this to describe a field.

```python
class SomeDescriptedAttribute(str, metaclass=MadType):
    annotation = str
    description = "Some description"
```

using `json_schema` on `SomeDescription` will include the description attribute

```python
class DescriptedString(str, metaclass=MadType):
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
At the moment it is not checked nor tested, and will probably render an invalid `json-schema` without warning nor error

```python

def test_pattern_definition_allows_normal_usage():
    class PhoneNumber(str, metaclass=MadType):
        annotation = str
        pattern = r"\d{3}-\d{3}-\d{4}"

    PhoneNumber("000-000-0000")


def test_pattern_raise_type_error():
    class PhoneNumber(str, metaclass=MadType):
        annotation = str
        pattern = r"\d{3}-\d{3}-\d{4}"

    with pytest.raises(TypeError):
        PhoneNumber("oops")


def test_pattern_is_rendered_in_json_schema():
    class PhoneNumber(str, metaclass=MadType):
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
    class Item(dict, metaclass=MadType):
        title: Optional[str]
        content: Optional[str]

        def is_valid(self, **kwargs):
            """title is mandatory if content is absent"""
            if not kwargs.get("content", None) and not kwargs.get(
                "title", None
            ):
                raise TypeError(
                    "Either `Title` or `Content` are mandatory for Item"
                )

    Item(
        title="foo"
    )  # we should be able to create with only one of title or content
    Item(content="foo")
    with pytest.raises(TypeError):
        Item()


```

- ### Multiple inheritance

It is possible to create a schema from existing schemas.

:warning: careful not to use MadType of sub-classes as this would trigger
and infinite recursion.

```python

def test_multiple_inheritance():
    class Foo(dict):
        foo: str

    class Bar(dict):
        bar: str

    class FooBar(Foo, Bar, metaclass=MadType):
        pass

    FooBar(foo="foo", bar="bar")
    with pytest.raises(TypeError):
        FooBar()
```

- ### Dynamicly remove a field

Fields can be removed.

```python


def test_fields_can_be_removed():
    @subtract_fields("name")
    class Foo(dict, metaclass=MadType):
        name: str
        age: int

    Foo(age=2)

```
[![Test](https://github.com/6r17/madtypes/actions/workflows/test.yaml/badge.svg)](./tests/test_schema.py)
[![pypi](https://img.shields.io/pypi/v/madtypes)](https://pypi.org/project/madtypes/)
![python: >3.10](https://img.shields.io/badge/python-%3E3.10-informational)
### Installation

```bash
pip3 install madtypes
```
