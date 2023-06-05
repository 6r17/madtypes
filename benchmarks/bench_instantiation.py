from madtypes import MadType


class Item(dict):
    name: str
    age: int


class MadItem(dict, metaclass=MadType):
    name: str
    age: int


def benchmark_simple():
    Item(name="name", age=2)


def benchmark_mad():
    MadItem(name="name", age=2)


__benchmarks__ = [(benchmark_simple, benchmark_mad, "Correct instantiation")]
