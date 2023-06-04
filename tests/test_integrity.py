import json
import pytest
from typing import Optional
from madtypes import MadType, subtract_fields
from enum import Enum


def test_simple_dict_incorrect_setattr():
    class Simple(dict):
        name: str

    Simple(name=2)
    a = Simple()
    a.simple = 5


class Person(dict, metaclass=MadType):
    name: str


def test_mad_dict_type_error_with_incorrect_creation():
    with pytest.raises(TypeError):
        Person(name=2)


def test_mad_dict_is_ok_with_correct_creation():
    Person(name="foo")


def test_mad_dict_type_error_with_incorrect_setattr():
    with pytest.raises(TypeError):
        person = Person(name="foo")
        person.name = 2


def test_mad_dict_is_ok_with_correct_setattr():
    person = Person(name="foo")
    person.name = "bar"


def test_mad_dict_type_error_with_extra_parameter():
    with pytest.raises(TypeError):
        Person(age=2)


def test_mad_dict_type_checks_enum():
    class Color(Enum):
        red = 1
        green = 2
        blue = 3

    class Car(dict, metaclass=MadType):
        color: Color

    Car(color=Color.red)
    with pytest.raises(TypeError):
        Car(color=1)
    with pytest.raises(TypeError):
        Car(color="something")


def test_mad_dict_type_error_with_incomplete_parameters():
    with pytest.raises(TypeError):
        Person()


class Opt(dict, metaclass=MadType):
    name: Optional[str]


def test_mad_dict_is_ok_with_optional_type():
    Opt()
    opt = Opt(name="foo")
    assert opt["name"] == "foo"
    assert opt.name == "foo"


def test_mad_dict_type_error__with_erronous_optional_type():
    with pytest.raises(TypeError):
        Opt(name=2)


def test_referenced_objects_json_dumps():
    class Foo(dict, metaclass=MadType):
        name: str

    class ComplexObject(dict, metaclass=MadType):
        name: str
        foo: Foo

    assert (
        json.dumps(ComplexObject(name="foo", foo=Foo(name="bar")))
        == '{"name": "foo", "foo": {"name": "bar"}}'
    )


def test_mad_dict_value_integrity():
    class Foo(dict, metaclass=MadType):
        name: str

    a = Foo(name="foo")
    b = Foo(name="baz")
    assert a.name == "foo"
    assert b.name == "baz"


@pytest.mark.parametrize("_type_", [str, int, float, bytes])
def test_mad_optional_primitive(_type_):
    class SomeType(_type_, metaclass=MadType):
        annotation = Optional[_type_]

    SomeType()


@pytest.mark.parametrize(
    "value",
    [(str, "correct"), (int, 2), (float, 2.4), (bytes, b"hello")],
    ids=["string", "int", "float", "bytes"],
)
def test_correct_mad_primitive(value):
    _type_, correct = value

    class SomeType(_type_, metaclass=MadType):
        annotation = _type_
        description = f"{_type_}"

    SomeType(correct)

    with pytest.raises(TypeError):
        SomeType()


@pytest.mark.parametrize(
    "value",
    [(str, 2), (int, "2"), (float, "2"), (bytes, "incorrect")],
    ids=["string", "int", "float", "bytes"],
)
def test_incorrect_mad_primitive(value):
    _type_, incorrect = value

    class SomeType(_type_, metaclass=MadType):
        annotation = _type_
        description = f"{_type_}"

    with pytest.raises(TypeError):
        SomeType(incorrect)


def test_heritage_from_existing_class():
    class Foo(dict):
        foo: str

    class MadFoo(Foo, metaclass=MadType):
        pass

    MadFoo(foo="name")


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


def test_custom_init_method_can_be_overwritten():
    class SmartBoy(dict, metaclass=MadType):
        foo: int

        def __init__(self, *__args__, **__kwargs__):
            self.foo = 5

    with pytest.raises(TypeError):  # foo is stil a mandatory key hehehe
        assert SmartBoy().foo == 2
    assert (
        SmartBoy(foo=2).foo == 5
    )  # value is correctly overwrriten by custom __init__


def test_custom_init_method_cannot_bypass_typecheck():
    class SmartBoy(dict, metaclass=MadType):
        foo: str

        def __init__(self, *__args__, **__kwargs__):
            self.foo = 2

    with pytest.raises(TypeError):
        SmartBoy()


def test_fields_can_be_removed():
    @subtract_fields("name")
    class Foo(dict, metaclass=MadType):
        name: str
        age: int

    Foo(age=2)


def test_pattern_definition_allows_normal_usage():
    class PhoneNumber(str, metaclass=MadType):
        annotation = str
        pattern = r"\d{3}-\d{3}-\d{4}"  # Regex pattern to match a phone number in the format XXX-XXX-XXXX

    PhoneNumber("000-000-0000")


def test_pattern_raise_type_error():
    class PhoneNumber(str, metaclass=MadType):
        annotation = str
        pattern = r"\d{3}-\d{3}-\d{4}"  # Regex pattern to match a phone number in the format XXX-XXX-XXXX

    with pytest.raises(TypeError):
        PhoneNumber("oops")


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
