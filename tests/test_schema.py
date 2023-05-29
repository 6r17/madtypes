from typing import Optional
from madtypes import schema, Schema, Annotation, Immutable
import pytest
import json


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
    a = Item(name="bar", gender=Gender(female=10, male=20))
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
    a = Item(name="bob", gender=Gender(male=20, female=30))
    a.gender = Gender(male=30, female=10)
    assert a.gender.male == 30
    with pytest.raises(TypeError):
        a.gender.male = "foo"


def test_int_schema():
    assert schema(int) == {"type": "integer"}


def test_array_schema():
    assert schema(list[int]) == {"type": "array", "items": {"type": "integer"}}


def test_tuple_schema():
    assert schema(tuple[int, int]) == {
        "type": "array",
        "items": [{"type": "integer"}, {"type": "integer"}],
    }


def test_object_schema():
    class Item(Schema):
        name: str

    assert schema(Item) == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }


def test_array_of_object_schema():
    class Item(Schema):
        name: str

    class Basket(Schema):
        items: list[Item]

    schem = schema(Basket)
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


def test_tuple_of_object_schema():
    class Item(Schema):
        name: str

    class Basket(Schema):
        some_items: tuple[Item, Item]

    schem = schema(Basket)
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


def test_object_with_object_schema():
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
                "required": ["female", "male"],
            },
        },
        "required": ["name", "gender"],
    }


class PrimitiveArray(Schema):
    items: list[str]


def test_annotation_array():
    assert schema(PrimitiveArray) == {
        "type": "object",
        "properties": {
            "items": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["items"],
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
        "required": ["descripted_array"],
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
                    "required": ["name"],
                },
            }
        },
        "required": ["persons"],
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
        "required": ["tupled"],
    }


def test_type_error():
    class Item(Schema):
        value: int

    with pytest.raises(TypeError):
        Item(value="foo")


def test_instantiation_type_error():
    class Item(Schema):
        value: int

    with pytest.raises(TypeError):
        Item(value="foo")  # any easy way to enable linter here ?


def test_complex_type_error():
    class Item(Schema):
        value: list[int]

    with pytest.raises(TypeError):
        Item(value=["str", "str"])


def test_schemas_are_reprable():
    class Item(Schema):
        value: str

    e = Item(value="test")
    assert repr(e) == "{'value': 'test'}"


def test_schemas_expect_types():
    class Item(Schema):
        value: "str"

    with pytest.raises(SyntaxError):
        schema(Item)


def test_immutable():
    class SomeImmutable(Immutable):
        name: str

    e = SomeImmutable(name="foo")
    with pytest.raises(TypeError):
        e.name = "bar"

    with pytest.raises(TypeError):
        e["name"] = "bar"


def test_copy():
    class SomeImmutable(Immutable):
        name: str
        age: int

    with pytest.raises(TypeError):
        a = SomeImmutable(name="foo")  # missing age

    class AnotherImmutable(Immutable):
        name: str
        age: Optional[int]

    a = AnotherImmutable(name="foo")
    b = AnotherImmutable(**a)
    assert b.name == "foo"
    c = SomeImmutable(age=2, **a)
    assert c.name == "foo"
    assert c.age == 2


def test_custom_method():
    class SomeClass(Schema):
        name: str

        def method(self) -> str:
            return self.name

    assert SomeClass(name="foo").method() == "foo"


def test_optional_json_schema():
    class SomeClassWithOptional(Schema):
        name: Optional[str]

    SomeClassWithOptional()
    schem = schema(SomeClassWithOptional)
    assert schem == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
    }


def test_optional_json_schema_with_array():
    class SomeClassWithOptional(Schema):
        elements: Optional[list[int]]

    SomeClassWithOptional()
    schem = schema(SomeClassWithOptional)
    assert schem == {
        "type": "object",
        "properties": {
            "elements": {"type": "array", "items": {"type": "integer"}}
        },
    }


def test_descripted_value_set():
    class SomeDescriptedField(str, metaclass=Annotation):
        description = "foo"
        annotation = str

    class SomeItem(Schema):
        name: SomeDescriptedField

    with pytest.raises(TypeError):
        SomeDescriptedField(2)
    a = SomeItem(name=SomeDescriptedField("foo"))
    assert a.name == "foo"
    a.name = SomeDescriptedField("bar")
    assert a == {"name": "bar"}
    assert json.dumps(a) == '{"name": "bar"}'
    assert a.name.description == "foo"


def test_descripted_list_value_set():
    class SomeDescriptedListField(list, metaclass=Annotation):
        description = "foo"
        annotation = list[str]

    class SomeListItem(Schema):
        names: SomeDescriptedListField

    values = SomeDescriptedListField(["1", "2", "3"])
    print(values)
    assert values == ["1", "2", "3"]
    with pytest.raises(TypeError):
        SomeListItem(names=SomeDescriptedListField([1]))
    a = SomeListItem(names=SomeDescriptedListField(["1", "2", "3"]))
    assert len(a.names) == 3
    assert json.dumps(a) == '{"names": ["1", "2", "3"]}'
    with pytest.raises(AttributeError):  # append does not exist
        a.append("foo")


def test_descripted_list_object_value_set():
    class Foo(Schema):
        name: str

    class DescriptedFoo(Foo, metaclass=Annotation):
        description = "description"
        annotation = Foo

    DescriptedFoo(name="foo")
    with pytest.raises(TypeError):
        DescriptedFoo(name=2)


def test_descripted_json_schema():
    class DescriptedString(str, metaclass=Annotation):
        description = "Some description"
        annotation = str

    class DescriptedItem(Schema):
        descripted: DescriptedString

    print(schema(DescriptedItem))
    assert schema(DescriptedItem) == {
        "type": "object",
        "properties": {
            "descripted": {
                "type": "string",
                "description": "Some description",
            },
        },
        "required": ["descripted"],
    }
