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


class Annotation(type):
    def __new__(cls, name, bases, attrs):
        # Retrieve the annotation from the class attributes
        annotation = attrs.get("annotation")
        pattern = attrs.get("pattern", None)

        # Override the __new__ method of the list class
        def new_method(cls, *values, **kwargs):
            # Check the type of each value before initializing
            if pattern and (annotation != str and annotation != bytes):
                raise SyntaxError(
                    f"pattern attribute can only be applied upon `str` or `bytes`, was `{annotation}`"
                )
            for value in values:
                if not type_check(value, annotation):
                    raise TypeError(
                        f"All values must be compatible with the annotation '{annotation}'"
                    )

                if pattern and not re.fullmatch(pattern, value):
                    raise TypeError(
                        f"`{values[0]}` did not match provided pattern `{pattern}`"
                    )

            # Create the instance and initialize it with the values
            instance = super(cls, cls).__new__(cls, *values, **kwargs)
            return instance

        # Assign the overridden __new__ method to the class
        attrs["__new__"] = new_method
        return super().__new__(cls, name, bases, attrs)


def subtract_fields(*fields):
    def decorator(cls):
        new_annotations = cls.__annotations__.copy()
        new_cls_dict = dict(cls.__dict__)

        for field in fields:
            if field in new_annotations:
                del new_annotations[field]
            if field in new_cls_dict:
                del new_cls_dict[field]  # pragma: no cover (tested by getattr)

        new_cls_dict["__annotations__"] = new_annotations

        new_cls = type(cls.__name__, cls.__bases__, new_cls_dict)
        return new_cls

    return decorator


class Schema(dict):
    @classmethod
    def get_fields(cls):
        fields = list(cls.__annotations__.items())

        # Check if the class inherits from another Schema
        for base in cls.__bases__:
            if issubclass(base, Schema):
                # Retrieve the fields from the parent class
                fields.extend(base.get_fields())

        return fields

    def __init__(self, **kwargs):
        fields = dict(self.get_fields())
        for key, value in kwargs.items():
            if key not in fields:
                raise TypeError(
                    f"{key} is not a key for {type(self).__name__}"
                )
        for key, value in fields.items():
            if key in kwargs:
                if type_check(kwargs[key], value):
                    super().__setitem__(key, kwargs[key])
                else:
                    raise TypeError(
                        f"{kwargs[key]} is not an instance of {value}"
                    )
            else:
                optional = is_optional_type(value)
                if not optional:
                    raise TypeError(f"{key} is a mandatory field")
        if not self.is_valid(**kwargs):
            raise TypeError(f"{kwargs} did not pass object validation")

    def is_valid(self, **__kwargs__) -> bool:
        """Validation at Object scope, for validation based on multiple fields."""
        return True

    def __getattr__(self, name):
        if name in self:
            return self[name]
        # I don't know how to trigger the next line, it's more of an `in-case'
        return super().__getattribute__(name)  # pragma: no cover

    def __setattr__(self, name, value):
        annotation = self.__annotations__[name]

        if not isinstance(value, annotation):
            raise TypeError(f"{value} is not an instance of {annotation}")
        self[name] = value

    @classmethod
    def required_fields(cls) -> list[str]:
        return [
            name
            for name, field in cls.get_fields()
            if not is_optional_type(field)
        ]


class Immutable(Schema):
    def __setattr__(self, __name__, __value__):
        raise TypeError("'Immutable' object does not support item assignment")

    def __setitem__(self, __key__, __value__):
        raise TypeError("'Immutable' object does not support item assignment")


def json_schema(
    annotation: Union[Type["Type"], Type["Annotation"], Type["Schema"]],
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

        if issubclass(origin, Schema):
            result.update(
                {
                    "type": "object",
                    "properties": {
                        name: json_schema(field)
                        for name, field in origin.get_fields()
                    },
                }
            )
            required = origin.required_fields()
            if len(required) > 0:
                result.update({"required": required})
        if getattr(origin, "annotation", False):
            extra = {
                key: value
                for key, value in origin.__dict__.items()
                if not callable(value) and not key.startswith("__")
            }
            return json_schema(origin.annotation, **extra)
    if is_optional_type(annotation):
        return json_schema(remove_optional(annotation))
    return result
