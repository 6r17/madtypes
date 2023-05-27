from typing import get_args, get_origin, Union, Type

TYPE_TO_STRING: dict[type, str] = {
    str: "string",
    int: "integer",
    list: "array",
    float: "number",
    tuple: "array",
}


class Annotation:
    annotation: Union[Type["Type"], Type["Annotation"], Type["Schema"]]
    description: str


class Schema(dict):
    def __init__(self, **kwargs):
        for key, value in self.__annotations__.items():
            if key in kwargs:
                if isinstance(kwargs[key], value):
                    super().__setitem__(key, kwargs[key])
                else:
                    raise TypeError(
                        f"{kwargs[key]} is not an instance of {value}"
                    )

    @classmethod
    def get_fields(cls):
        return list(cls.__annotations__.items())

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        annotation = self.__annotations__[name]
        annotation = (
            annotation.annotation
            if isinstance(
                annotation,
                Annotation,
            )
            else annotation
        )
        if not isinstance(value, annotation):
            raise TypeError(f"{value} is not an instance of {annotation}")
        self[name] = value


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
    print(origin)
    if not isinstance(origin, type):
        raise SyntaxError("A typing annotation has been written as Literal")
    if issubclass(origin, Schema):
        result.update(
            {
                "type": "object",
                "properties": {
                    name: schema(field) for name, field in origin.get_fields()
                },
            }
        )
    if issubclass(origin, Annotation):
        extra = {
            key: value
            for key, value in origin.__dict__.items()
            if not callable(value) and not key.startswith("__")
        }
        try:
            del extra["annotation"]
        except KeyError:
            pass
        return schema(origin.annotation, **extra)
    return result
