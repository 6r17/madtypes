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
