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
