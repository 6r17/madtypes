from typing import get_args, get_origin, Union, Type
import inspect

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

    print("origin:", origin)
    print("args:", args)
    print("value:", value)
    if origin is None:
        # Non-generic type
        return isinstance(value, annotation)
    elif origin is list or origin is set or origin is Union:
        print("sub annotation", args)
        # typing.Union cannot be used by is_instance
        if is_optional_type(annotation):
            inner_annotation = args[0]
            print(
                ">>",
                inner_annotation,
                value,
                type_check(value, inner_annotation),
            )
            return type_check(value, inner_annotation)
        elif isinstance(value, origin):
            if args:
                # Parametrized list annotation
                inner_annotation = args[0]
                print(inner_annotation)
                return all(
                    type_check(item, inner_annotation) for item in value
                )


class Annotation(type):
    def __new__(cls, name, bases, attrs):
        # Retrieve the annotation from the class attributes
        annotation = attrs.get("annotation")

        # Override the __new__ method of the list class
        def new_method(cls, *values, **kwargs):
            # Check the type of each value before initializing the list
            for value in values:
                if not type_check(value, annotation):
                    raise TypeError(
                        f"All values must be compatible with the annotation '{annotation}'"
                    )

            # Create the list instance and initialize it with the values
            instance = super(cls, cls).__new__(cls, *values, **kwargs)
            return instance

        # Assign the overridden __new__ method to the class
        attrs["__new__"] = new_method
        return super().__new__(cls, name, bases, attrs)


class Schema(dict):
    def __init__(self, **kwargs):
        for key, value in self.__annotations__.items():
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

    @classmethod
    def get_fields(cls):
        return list(cls.__annotations__.items())

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
            for name, field in cls.__annotations__.items()
            if not is_optional_type(field)
        ]


class Immutable(Schema):
    def __setattr__(self, __name__, __value__):
        raise TypeError("'Immutable' object does not support item assignment")

    def __setitem__(self, __key__, __value__):
        raise TypeError("'Immutable' object does not support item assignment")


def schema(
    annotation: Union[Type["Type"], Type["Annotation"], Type["Schema"]],
    **kwargs,
) -> dict:
    result = kwargs
    origin = get_origin(annotation)
    origin = annotation if not origin else origin
    args = get_args(annotation)
    if origin in TYPE_TO_STRING:
        result.update({"type": TYPE_TO_STRING[origin]})
    if origin == list:
        result.update({"items": schema(args[0])})
    if origin == tuple:
        result.update({"items": [schema(arg) for arg in args]})
    if isinstance(origin, str):
        raise SyntaxError("A typing annotation has been written as Literal")
    if inspect.isclass(origin):
        if issubclass(origin, Schema):
            result.update(
                {
                    "type": "object",
                    "properties": {
                        name: schema(field)
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
            return schema(origin.annotation, **extra)
    if is_optional_type(annotation):
        return schema(remove_optional(annotation))
    return result
