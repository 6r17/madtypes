from typing import get_args, get_origin, Union, Type
from enum import Enum
import inspect
import re

TYPE_TO_STRING: dict[type, str] = {
    str: "string",
    int: "integer",
    list: "array",
    float: "number",
    tuple: "array",
}


def is_optional_type(annotation):
    return getattr(annotation, "__origin__", None) is Union and type(
        None
    ) in getattr(annotation, "__args__", ())


def remove_optional(typing_annotation):
    return get_args(typing_annotation)[0]


def type_check(value, annotation):
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is None:
        # Non-generic type
        return isinstance(value, annotation)
    elif origin is list or origin is set or origin is Union:
        # typing.Union cannot be used by is_instance
        if is_optional_type(annotation):
            inner_annotation = args[0]
            return type_check(value, inner_annotation)
        elif isinstance(value, origin):
            if args:
                # Parametrized list annotation
                inner_annotation = args[0]
                return all(
                    type_check(item, inner_annotation) for item in value
                )


def dict_getattr(self, name):
    if name in self:
        return self[name]
    # I don't know how to trigger the next line, it's more of an `in-case'
    return super().__getattribute__(name)  # pragma: no cover


def dict_setattr(self, name, value):
    annotation = self.__annotations__[name]

    if not isinstance(value, annotation):
        raise TypeError(f"{value} is not an instance of {annotation}")
    self[name] = value


def return_true(*__args__, **__kwargs__) -> bool:
    return True


class Annotation(type):
    def get_fields(cls):
        fields = list(cls.__annotations__.items())
        # Check if the class inherits from another Schema
        for base in cls.__bases__:
            if issubclass(base, Annotation):
                # Retrieve the fields from the parent class
                fields.extend(base.get_fields())

        return fields

    def required_fields(cls) -> list[str]:
        return [
            name
            for name, field in cls.get_fields()
            if not is_optional_type(field)
        ]

    def __new__(cls, name, bases, attrs):
        # Retrieve the annotation from the class attributes
        annotation = attrs.get("annotation")
        pattern = attrs.get("pattern")

        # Override the __new__ method
        def new_method(cls, *values, **kwargs):
            # Check the type of each value before initializing
            nonlocal annotation
            for value in values:
                if not type_check(value, annotation):
                    raise TypeError(
                        f"All values must be compatible with the annotation '{annotation}'"
                    )
                if (
                    pattern
                    and (annotation == str or annotation == bytes)
                    and not re.fullmatch(pattern, value)
                ):
                    raise TypeError(
                        f"`{values[0]}` did not match provided pattern `{pattern}`"
                    )
            if cls.__bases__[0] == dict:
                for name, annotation in cls.__annotations__.items():
                    if name in kwargs:
                        if not type_check(kwargs[name], annotation):
                            raise TypeError(
                                f"{kwargs[name]} is not an instance of {annotation}"
                            )
                    else:
                        if not is_optional_type(annotation):
                            raise TypeError(
                                f"{name} is mandatory {annotation} of {cls}"
                            )
                    if not cls.is_valid():
                        raise TypeError(
                            f"{kwargs[name]} is not valid by `is_valid` function"
                        )
                for name, value in kwargs.items():
                    if name not in cls.__annotations__:
                        raise TypeError(f"{name} is not a valid key for {cls}")
            # Create the instance and initialize it with the values
            instance = super(cls, cls).__new__(cls, *values, **kwargs)
            return instance

        # Assign the overridden __new__ method to the class
        attrs["__new__"] = new_method
        if bases[0] == dict:
            attrs["__getattr__"] = dict_getattr
            attrs["__setattr__"] = dict_setattr
            if not attrs.get("is_valid", None):
                attrs["is_valid"] = return_true
        return super().__new__(cls, name, bases, attrs)


def remove_fields(*args):
    def decorator(cls):
        for field_name in args:
            # Remove the field
            if hasattr(cls, field_name):
                delattr(cls, field_name)

            # Remove the annotation (if any)
            if (
                hasattr(cls, "__annotations__")
                and field_name in cls.__annotations__
            ):
                cls.__annotations__.pop(field_name)

        return cls

    return decorator


def json_schema(
    annotation: Union[Type["Type"], Type["Annotation"]],
    **kwargs,
) -> dict:
    result = kwargs
    origin = get_origin(annotation)
    origin = annotation if not origin else origin
    args = get_args(annotation)
    if origin in TYPE_TO_STRING:
        result.update({"type": TYPE_TO_STRING[origin]})
    if origin == list or origin == set:
        result.update({"type": "array", "items": json_schema(args[0])})
    if origin == set:
        result.update({"uniqueItems": True})
    if origin == tuple:
        result.update({"items": [json_schema(arg) for arg in args]})
    if isinstance(origin, str):
        raise SyntaxError("A typing annotation has been written as Literal")
    if inspect.isclass(origin):
        if issubclass(origin, Enum):
            first_enum_member = next(iter(origin))
            enum_type = TYPE_TO_STRING[type(first_enum_member.value)]
            result.update(
                {
                    "type": enum_type,
                    "enum": [enu.value for enu in iter(origin)],
                }
            )
            return result
        if getattr(origin, "annotation", False):
            extra = {
                key: value
                for key, value in origin.__dict__.items()
                if not callable(value) and not key.startswith("__")
            }
            return json_schema(origin.annotation, **extra)
        elif issubclass(origin, dict):
            result.update(
                {
                    "type": "object",
                    "properties": {
                        name: json_schema(annotation)
                        for name, annotation in origin.__annotations__.items()
                    },
                }
            )

            required = origin.required_fields()
            if len(required) > 0:
                result.update({"required": required})

            return result
    if is_optional_type(annotation):
        return json_schema(remove_optional(annotation))
    return result
