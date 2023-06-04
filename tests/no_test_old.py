from enum import Enum
from typing import Optional
from madtypes import (
    json_schema,
    Annotation,
    type_check,
    remove_fields,
)
import pytest
import json


class Gender(dict, metaclass=Annotation):
    female: int
    male: int


class Item(dict, metaclass=Annotation):
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


def test_set():
    a = Item(name="bob", gender=Gender(male=20, female=30))
    a.gender = Gender(male=30, female=10)
    assert a.gender.male == 30
    with pytest.raises(TypeError):
        a.gender.male = "foo"


def test_extra_parameter():
    class Foo(dict, metaclass=Annotation):
        pass

    with pytest.raises(TypeError):
        Foo(name="foo")


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
    class Item(dict, metaclass=Annotation):
        name: str

    assert json_schema(Item) == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }


def test_array_of_object_json_schema():
    class Item(dict, metaclass=Annotation):
        name: str

    class Basket(dict, metaclass=Annotation):
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
    class Item(dict, metaclass=Annotation):
        name: str

    class Basket(dict, metaclass=Annotation):
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
    print(json_schema(Item))
    assert json_schema(Item) == {
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


class PrimitiveArray(dict, metaclass=Annotation):
    items: list[str]


def test_annotation_array():
    assert json_schema(PrimitiveArray) == {
        "type": "object",
        "properties": {
            "items": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["items"],
    }


class PrimitiveDescriptiveArray(list, metaclass=Annotation):
    annotation = list[int]
    description = "some description"


class PrimitiveDescriptedArray(dict, metaclass=Annotation):
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


class Person(dict, metaclass=Annotation):
    name: str


class ObjectArray(dict, metaclass=Annotation):
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


class DescriptiveName(str, metaclass=Annotation):
    annotation = str
    description = "How you'd call the beer"


class Beer(dict, metaclass=Annotation):
    name: DescriptiveName


class ObjectDescriptiveArray(list, metaclass=Annotation):
    annotation = list[Beer]
    description = "Lots of beers"


class ObjectDescriptedArray(dict, metaclass=Annotation):
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


class PrimitiveTuple(dict, metaclass=Annotation):
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


def test_type_error():
    class Item(dict, metaclass=Annotation):
        value: int

    with pytest.raises(TypeError):
        Item(value="foo")


def test_instantiation_type_error():
    class Item(dict, metaclass=Annotation):
        value: int

    with pytest.raises(TypeError):
        Item(value="foo")  # any easy way to enable linter here ?


def test_complex_type_error():
    class Item(dict, metaclass=Annotation):
        value: list[int]

    with pytest.raises(TypeError):
        Item(value=["str", "str"])


def test_schemas_are_reprable():
    class Item(dict, metaclass=Annotation):
        value: str

    e = Item(value="test")
    assert repr(e) == "{'value': 'test'}"


def test_schemas_expect_types():
    class Item(dict, metaclass=Annotation):
        value: "str"

    with pytest.raises(SyntaxError):
        json_schema(Item)


def test_custom_method():
    class SomeClass(dict, metaclass=Annotation):
        name: str

        def method(self) -> str:
            return self.name

    assert SomeClass(name="foo").method() == "foo"


def test_optional_json_schema():
    class SomeClassWithOptional(dict, metaclass=Annotation):
        name: Optional[str]

    SomeClassWithOptional()
    schem = json_schema(SomeClassWithOptional)
    assert schem == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
    }


def test_optional_json_schema_with_array():
    class SomeClassWithOptional(dict, metaclass=Annotation):
        elements: Optional[list[int]]

    SomeClassWithOptional()
    schem = json_schema(SomeClassWithOptional)
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

    class SomeItem(dict, metaclass=Annotation):
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

    class SomeListItem(dict, metaclass=Annotation):
        names: SomeDescriptedListField

    values = SomeDescriptedListField(["1", "2", "3"])
    print(values)
    assert values == ["1", "2", "3"]
    with pytest.raises(TypeError):
        SomeListItem(names=SomeDescriptedListField([1]))
    a = SomeListItem(names=SomeDescriptedListField(["1", "2", "3"]))
    assert len(a.names) == 3
    assert json.dumps(a) == '{"names": ["1", "2", "3"]}'


def test_descripted_list_object_value_set():
    class DescriptedFoo(dict, metaclass=Annotation):
        description = "description"
        name: str

    DescriptedFoo(name="foo")
    with pytest.raises(TypeError):
        DescriptedFoo(name=2)


def test_descripted_json_json_schema():
    class DescriptedString(str, metaclass=Annotation):
        description = "Some description"
        annotation = str

    class DescriptedItem(dict, metaclass=Annotation):
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


def test_object_validation():
    class Item(dict, metaclass=Annotation):  # TODO
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


def test_set_set():
    class Basket(dict, metaclass=Annotation):
        content: set[int]

    Basket(content={1, 2, 3})


def test_type_check_primitive():
    assert type_check(1, int)


def test_type_check_list_of_primitive():
    assert type_check([1, 2], list[int])


def test_type_check_set_of_primitive():
    assert type_check({1}, set[int])


def test_type_check_optional_primitive():
    assert type_check(1, Optional[int])
    assert type_check("foo", Optional[int]) == False


def test_pattern_definition_allows_normal_usage():
    class PhoneNumber(str, metaclass=Annotation):
        annotation = str
        pattern = r"\d{3}-\d{3}-\d{4}"  # Regex pattern to match a phone number in the format XXX-XXX-XXXX

    PhoneNumber("000-000-0000")


def test_pattern_raise_type_error():
    class PhoneNumber(str, metaclass=Annotation):
        annotation = str
        pattern = r"\d{3}-\d{3}-\d{4}"  # Regex pattern to match a phone number in the format XXX-XXX-XXXX

    with pytest.raises(TypeError):
        PhoneNumber("oops")


def test_pattern_is_rendered_in_json_schema():
    class PhoneNumber(str, metaclass=Annotation):
        annotation = str
        pattern = r"^\d{3}-\d{3}-\d{4}$"
        description = "A phone number in the format XXX-XXX-XXXX"

    class Contact(dict, metaclass=Annotation):
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


def test_dict_objet_keep_annotations():
    class Foo(dict):
        foo: str

    assert len(Foo.__annotations__) == 1


def test_list_json_schema():
    class Foo(dict, metaclass=Annotation):
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
    class Foo(dict, metaclass=Annotation):
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

    class Item(dict, metaclass=Annotation):
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


def test_class_field_subtraction():
    class Item(dict, metaclass=Annotation):
        name: str
        age: int

    AgeLessItem = remove_fields("age")(Item)
    assert len(AgeLessItem.get_fields()) == 1
    print(AgeLessItem.get_fields())
    with pytest.raises(TypeError):
        AgeLessItem(name="foo", age=2)
    AgeLessItem(name="foo")
    print(AgeLessItem)
    with pytest.raises(AttributeError):
        assert getattr(Item, "age")


def test_json_schema_after_subtraction():
    class Item(dict, metaclass=Annotation):  # TODO
        name: str
        age: int

    ageLessItem = remove_fields("age")(Item)
    schema = json_schema(ageLessItem)
    assert schema == {}


def test_annotated_dict():
    class Foo(dict, metaclass=Annotation):
        name: str

    schema = json_schema(Foo)
    print(schema)
    assert schema == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }


def test_multiple_inheritance_json_schema():
    class Foo(dict, metaclass=Annotation):
        foo: str

    class Bar(dict, metaclass=Annotation):
        bar: str

    class FooBar(Foo, Bar):
        pass

    assert len(FooBar.get_fields()) == 2
    schema = json_schema(FooBar)
    print(schema)
    assert schema == {
        "type": "object",
        "properties": {"foo": {"type": "string"}, "bar": {"type": "string"}},
        "required": ["foo", "bar"],
    }


def test_multiple_inheritance_integrity():
    class Foo(dict, metaclass=Annotation):
        foo: str

    class Bar(dict, metaclass=Annotation):
        bar: str

    class FooBar(Foo, Bar):
        pass

    FooBar(foo="foo", bar="bar")


def test_json_schema_after_edition_and_multiple_inheritance():
    class Person(dict, metaclass=Annotation):
        name: str
        age: int

    class Contact(dict, metaclass=Annotation):
        phone: str

    agelessPerson = remove_fields("age")(Person)

    class NamedContact(agelessPerson, Contact):
        pass

    NamedContact(name="foo", phone="baz")


def test_annotated_dict_type_check():
    class Foo(dict, metaclass=Annotation):
        name: str

    Foo(name="bar")
    with pytest.raises(TypeError):
        Foo()


def test_annotated_dict_value_integrity():
    class Foo(dict, metaclass=Annotation):
        name: str

    a = Foo(name="bar")
    assert a["name"] == "bar"
    b = Foo(name="boz")
    assert a["name"] == "bar"
    assert b["name"] == "boz"
    assert a.name == "bar"
    a.name = "test"
    assert a.name == "test"