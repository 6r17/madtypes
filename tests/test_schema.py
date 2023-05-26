from madtypes import schema, Schema, Annotation
import pytest


class Gender(Schema):
    female: int
    male: int


class Item(Schema):
    name: str
    gender: Gender


def test_dict_access():
    a = Item(name="foo", gender=Gender(female=10, male=20))
    print(a)
    assert a["name"] == "foo"


def test_get_fields():
    fields = Item.get_fields()
    print(fields)
    assert fields[0][0] == "name"


def test_attribute_access():
    a = Item(name="foo", gender=Gender(female=10, male=20))
    print(a)
    assert a.name == "foo"
    assert a["name"] == "foo"


def test_attribute_set():
    a = Item()
    a.name = "foo"
    assert a.name == "foo"
    assert a["name"] == "foo"


def test_json_dumps():
    import json

    a = Item(name="foo", gender=Gender(female=10, male=20))
    print(a)
    assert (
        json.dumps(a)
        == '{"name": "foo", "gender": {"female": 10, "male": 20}}'
    )


def test_json_dumps_and_load():
    import json

    a = Item(name="foo", gender=Gender(female=10, male=20))
    print(a)
    assert json.loads(json.dumps(a)) == a


def test_set():
    a = Item()
    with pytest.raises(AttributeError):
        a.gender.male = 20
    a.gender = Gender()
    a.gender.male = 20
    print(a)
    assert a.gender.male == 20


def test_int():
    assert schema(int) == {"type": "integer"}


def test_array():
    assert schema(list[int]) == {"type": "array", "items": {"type": "integer"}}


def test_tuple():
    assert schema(tuple[int, int]) == {
        "type": "array",
        "items": [{"type": "integer"}, {"type": "integer"}],
    }


def test_object():
    class Item(Schema):
        name: str

    assert schema(Item) == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
    }


def test_array_of_object():
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


def test_tuple_of_object():
    class Item(Schema):
        name: str

    class Basket(Schema):
        some_items: tuple[Item, Item]

    assert schema(Basket) == {
        "type": "object",
        "properties": {
            "some_items": {
                "type": "array",
                "items": [
                    {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    },
                    {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    },
                ],
            }
        },
    }


def test_json_schema():
    print(schema(Item))
    assert schema(Item) == {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "gender": {
                "type": "object",
                "properties": {
                    "female": {"type": "integer"},
                    "male": {"type": "integer"},
                },
            },
        },
    }


class DescriptedString(Annotation):
    description = "Some description"
    annotation = str


class DescriptedItem(Schema):
    descripted: DescriptedString


def test_descripted_json_schema():
    print(schema(DescriptedItem))
    assert schema(DescriptedItem) == {
        "type": "object",
        "properties": {
            "descripted": {
                "type": "string",
                "description": "Some description",
            },
        },
    }


class PrimitiveArray(Schema):
    items: list[str]


def test_annotation_array():
    assert schema(PrimitiveArray) == {
        "type": "object",
        "properties": {
            "items": {"type": "array", "items": {"type": "string"}}
        },
    }


class PrimitiveDescriptiveArray(Annotation):
    annotation = list[int]
    description = "some description"


class PrimitiveDescriptedArray(Schema):
    descripted_array: PrimitiveDescriptiveArray


def test_descriptive_primitive_array():
    result = schema(PrimitiveDescriptedArray)
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
    }


class Person(Schema):
    name: str


class ObjectArray(Schema):
    persons: list[Person]


def test_object_array():
    result = schema(ObjectArray)
    print(result)
    assert result == {
        "type": "object",
        "properties": {
            "persons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                },
            }
        },
    }


class DescriptiveName(Annotation):
    annotation = str
    description = "How you'd call the beer"


class Beer(Schema):
    name: DescriptiveName


class ObjectDescriptiveArray(Annotation):
    annotation = list[Beer]
    description = "Lots of beers"


class ObjectDescriptedArray(Schema):
    descripted_array: ObjectDescriptiveArray


def test_descriptive_object_array():
    result = schema(ObjectDescriptedArray)
    print(result)
    assert result == {
        "type": "object",
        "properties": {
            "descripted_array": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "How you'd call the beer",
                        }
                    },
                },
                "description": "Lots of beers",
            },
        },
    }


class PrimitiveTuple(Schema):
    tupled: tuple[int, str]


def test_annotation_tuple_schema():
    result = schema(PrimitiveTuple)
    print(result)
    assert result == {
        "type": "object",
        "properties": {
            "tupled": {
                "type": "array",
                "items": [{"type": "integer"}, {"type": "string"}],
            }
        },
    }


def test_type_error():
    class Item(Schema):
        value: int

    e = Item()
    with pytest.raises(TypeError):
        e.value = "foo"


def test_complex_type_error():
    class Item(Schema):
        value: list[int]

    e = Item()
    with pytest.raises(TypeError):
        e.value = ["str", "str"]


def test_schemas_are_reprable():
    class Item(Schema):
        value: str

    e = Item(value="test")
    assert repr(e) == "{'value': 'test'}"
