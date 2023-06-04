import pytest
import json
from enum import Enum
from madtypes import json_schema, MadType


def test_int_json_schema():
    assert json_schema(int) == {"type": "integer"}


def test_array_json_schema():
    assert json_schema(list[int]) == {
        "type": "array",
        "items": {"type": "integer"},
    }


def test_tuple_json_schema():
    assert json_schema(tuple[int, int]) == {
        "type": "array",
        "items": [{"type": "integer"}, {"type": "integer"}],
    }


def test_object_json_schema():
    class Item(dict, metaclass=MadType):
        name: str

    assert json_schema(Item) == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }


def test_array_of_object_json_schema():
    class Item(dict, metaclass=MadType):
        name: str

    class Basket(dict, metaclass=MadType):
        items: list[Item]

    schem = json_schema(Basket)
    print(schem)
    assert schem == {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            }
        },
        "required": ["items"],
    }


def test_tuple_of_object_json_schema():
    class Item(dict, metaclass=MadType):
        name: str

    class Basket(dict, metaclass=MadType):
        some_items: tuple[Item, Item]

    schem = json_schema(Basket)
    print(schem)
    assert schem == {
        "type": "object",
        "properties": {
            "some_items": {
                "type": "array",
                "items": [
                    {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"],
                    },
                    {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"],
                    },
                ],
            }
        },
        "required": ["some_items"],
    }


def test_object_with_object_json_schema():
    class SubItem(dict, metaclass=MadType):
        name: str

    class Item(dict, metaclass=MadType):
        sub: SubItem

    print(json_schema(Item))
    assert json_schema(Item) == {
        "type": "object",
        "properties": {
            "sub": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            }
        },
        "required": ["sub"],
    }


class PrimitiveArray(dict, metaclass=MadType):
    items: list[str]


def test_annotation_array():
    assert json_schema(PrimitiveArray) == {
        "type": "object",
        "properties": {
            "items": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["items"],
    }


class PrimitiveDescriptiveArray(list, metaclass=MadType):
    annotation = list[int]
    description = "some description"


class PrimitiveDescriptedArray(dict, metaclass=MadType):
    descripted_array: PrimitiveDescriptiveArray


def test_descriptive_primitive_array():
    result = json_schema(PrimitiveDescriptedArray)
    print(result)
    assert result == {
        "type": "object",
        "properties": {
            "descripted_array": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "some description",
            },
        },
        "required": ["descripted_array"],
    }


class Person(dict, metaclass=MadType):
    name: str


class ObjectArray(dict, metaclass=MadType):
    persons: list[Person]


def test_object_array():
    result = json_schema(ObjectArray)
    print(result)
    assert result == {
        "type": "object",
        "properties": {
            "persons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            }
        },
        "required": ["persons"],
    }


class DescriptiveName(str, metaclass=MadType):
    annotation = str
    description = "How you'd call the beer"


class Beer(dict, metaclass=MadType):
    name: DescriptiveName


class ObjectDescriptiveArray(list, metaclass=MadType):
    annotation = list[Beer]
    description = "Lots of beers"


class ObjectDescriptedArray(dict, metaclass=MadType):
    descripted_array: ObjectDescriptiveArray


def test_descriptive_object_array_json_schema():
    result = json_schema(ObjectDescriptedArray)
    print(result)
    assert result == {
        "type": "object",
        "properties": {
            "descripted_array": {
                "description": "Lots of beers",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "description": "How you'd call the beer",
                            "type": "string",
                        }
                    },
                    "required": ["name"],
                },
            }
        },
        "required": ["descripted_array"],
    }


class PrimitiveTuple(dict, metaclass=MadType):
    tupled: tuple[int, str]


def test_annotation_tuple_json_schema():
    result = json_schema(PrimitiveTuple)
    print(result)
    assert result == {
        "type": "object",
        "properties": {
            "tupled": {
                "type": "array",
                "items": [{"type": "integer"}, {"type": "string"}],
            }
        },
        "required": ["tupled"],
    }


def test_schemas_are_reprable():
    class Item(dict, metaclass=MadType):
        value: str

    e = Item(value="test")
    assert repr(e) == "{'value': 'test'}"


def test_descripted_json_schema():
    class DescriptedString(str, metaclass=MadType):
        description = "Some description"
        annotation = str

    class DescriptedItem(dict, metaclass=MadType):
        descripted: DescriptedString

    print(json_schema(DescriptedItem))
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


def test_list_json_schema():
    class Foo(dict, metaclass=MadType):
        my_set: list[int]

    schema = json_schema(Foo)
    print(schema)
    assert schema == {
        "type": "object",
        "properties": {
            "my_set": {
                "type": "array",
                "items": {"type": "integer"},
            }
        },
        "required": ["my_set"],
    }


def test_set_json_schema():
    class Foo(dict, metaclass=MadType):
        my_set: set[int]

    schema = json_schema(Foo)
    print(json.dumps(schema, indent=4))
    assert schema == {
        "type": "object",
        "properties": {
            "my_set": {
                "type": "array",
                "items": {"type": "integer"},
                "uniqueItems": True,
            }
        },
        "required": ["my_set"],
    }
    with pytest.raises(TypeError):
        Foo(my_set=[1, 2, 3])
    Foo(my_set={1, 2, 3})


def test_enum():
    class SomeEnum(Enum):
        FOO = "Foo"
        BAR = "Bar"
        BAZ = "Baz"

    class Item(dict, metaclass=MadType):
        key: SomeEnum

    schema = json_schema(Item)
    print(schema)
    assert schema == {
        "type": "object",
        "properties": {
            "key": {"type": "string", "enum": ["Foo", "Bar", "Baz"]}
        },
        "required": ["key"],
    }
    Item(key=SomeEnum.FOO)
    with pytest.raises(TypeError):
        Item(key="Foo")


def test_pattern_is_rendered_in_json_schema():
    class PhoneNumber(str, metaclass=MadType):
        annotation = str
        pattern = r"^\d{3}-\d{3}-\d{4}$"
        description = "A phone number in the format XXX-XXX-XXXX"

    class Contact(dict, metaclass=MadType):
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
