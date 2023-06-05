from madtypes import MadType


class Item(dict):
    name: str
    age: int

    def __init__(self, *__args__, **kwargs):
        for key, value in kwargs.items():
            if key not in self.__annotations__:
                raise TypeError("")
            if not isinstance(value, self.__annotations__[key]):
                raise TypeError()


class MadItem(dict, metaclass=MadType):
    name: str
    age: int


def benchmark_simple():
    try:
        Item(name="name", age=2, unknown="foo")
    except:
        pass


def benchmark_mad():
    try:
        MadItem(name="name", age=2, unknown="foo")
    except:
        pass


__benchmarks__ = [(benchmark_mad, benchmark_simple, "Incorrect instantiation")]
