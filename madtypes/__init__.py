import re
from enum import Enum
from typing import get_args, get_origin, Union, Type
import inspect


def DOES_NOTHING(__self__, *__values__, **__keyvalues__):
    pass


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


def generate_annotations_dict(cls):
    annotations_dict = cls.__annotations__

    for base in cls.__bases__:
        if hasattr(base, "__annotations__"):
            for key, value in base.__annotations__.items():
                if key in annotations_dict and annotations_dict[key] != value:
                    raise SyntaxError(
                        f"Conflicting annotations for key '{key}' in base classes"
                    )
                annotations_dict[key] = value

    return annotations_dict


def typecheck_dict_initialization(method):
    """Decorator for dict.__init__"""

    def wrapper(self, *values, **key_values):
        # todo:
        # values make no sense in dict except for user defined behavior
        # in which case type_check should be applied using the method annotation

        _annotations_ = generate_annotations_dict(self.__class__)

        for key, value in key_values.items():
            if key not in _annotations_:
                raise TypeError(f"{key} is not part of {self.__class__}")
            elif not type_check(value, _annotations_[key]):
                raise TypeError(
                    f"{value} is not compatible with {_annotations_[key]}"
                )
        for key, value in _annotations_.items():
            if key not in key_values:
                if not is_optional_type(value):
                    raise TypeError(
                        f"{key} is mandatory key of {self.__class__}"
                    )

        if getattr(self, "is_valid", False):
            self.is_valid(*values, **key_values)
        if method != DOES_NOTHING:
            # if user overwrites __init__ it is up to him to super
            method(self, *values, **key_values)
        else:
            super(self.__class__, self).__init__(*values, **key_values)

    return wrapper


def subtract_fields(*fields):
    def decorator(cls):
        new_annotations = cls.__annotations__.copy()
        new_cls_dict = dict(cls.__dict__)

        for field in fields:
            if field in new_annotations:
                del new_annotations[field]

        new_cls_dict["__annotations__"] = new_annotations

        new_cls = type(cls.__name__, cls.__bases__, new_cls_dict)
        return new_cls

    return decorator


def insert_typecheck_for(_type_):
    def typecheck_primitive_initialization(method):
        """Decorator for string.__init__"""

        def wrapper(self, *values, **key_values):
            if method != DOES_NOTHING:
                method(*values, **key_values)
            else:
                if (
                    (_type_ == str or _type_ == bytes)
                    and getattr(self, "pattern", False)
                    and (
                        not values[0]
                        or not re.fullmatch(
                            getattr(self, "pattern"), values[0]
                        )
                    )
                ):
                    if len(values) != 0:
                        raise TypeError(
                            f"{values[0]} did not match {self.pattern}"
                        )

                annotation = self.annotation if self.annotation else _type_
                if len(values) == 0:
                    if is_optional_type(annotation):
                        _type_.__init__(None)
                    else:
                        raise TypeError(
                            "Value mandatory for annotation {annotation}"
                        )
                elif not type_check(values[0], annotation):
                    raise TypeError(
                        "Value `{values[0]}` is not compatible with `{annotation}`"
                    )

        return wrapper

    return typecheck_primitive_initialization


def __getattr__(self, name):
    if name in self:
        return self[name]
    return super(self.__class__).__getattribute__(name)


def __setattr__(self, name, value):
    if not type_check(value, self.__annotations__[name]):
        raise TypeError(
            f"value `{value}` does not fit {self.__annotations__[name]} for key {name}"
        )
    self[name] = value


resolution = {
    dict: {
        "__init__": typecheck_dict_initialization,
    },
    str: {"__init__": insert_typecheck_for(str)},
    int: {"__init__": insert_typecheck_for(int)},
    float: {"__init__": insert_typecheck_for(float)},
}


@classmethod
def required_fields(cls) -> list[str]:
    return [
        name
        for name, field in cls.get_fields().items()
        if not is_optional_type(field)
    ]


@classmethod
def get_fields(cls):
    return generate_annotations_dict(cls)


class MadType(type):
    def __new__(cls, name, bases, attributes):
        # type is considered the first of bases
        # it is not supported to inherit from different types
        _type_ = bases[0]
        if _type_ == dict or issubclass(_type_, dict):
            attributes["__getattr__"] = __getattr__
            attributes["__setattr__"] = __setattr__
            attributes["__init__"] = typecheck_dict_initialization(
                attributes.get("__init__", DOES_NOTHING)
            )
            attributes["required_fields"] = required_fields
            attributes["get_fields"] = get_fields
        else:
            attributes["__init__"] = insert_typecheck_for(_type_)(
                attributes.get("__init__", DOES_NOTHING)
            )
        return super().__new__(cls, name, bases, attributes)


TYPE_TO_STRING: dict[type, str] = {
    str: "string",
    int: "integer",
    list: "array",
    float: "number",
    tuple: "array",
}


def json_schema(
    annotation: Type["Type"],
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
