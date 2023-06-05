from madtypes import MadType
import timeit


class Item(dict):
    name: str
    age: int


class MadItem(dict, metaclass=MadType):
    name: str
    age: int


def test_benchmark_simple():
    """MadType instantiation is about 20 times slower than pure python."""

    def benchmark_simple():
        Item(name="name", age=2)

    dict_time = timeit.timeit(benchmark_simple, number=10000)
    print(f"Dict time: {dict_time:.5f} miliseconds")

    def benchmark_mad():
        MadItem(name="name", age=2)

    mad_time = timeit.timeit(benchmark_mad, number=10000)

    print(f"Mad dict time: {mad_time:.5f} miliseconds")

    proportion = round(mad_time / dict_time)
    print(
        f"MadType instanciation is {proportion} times slower than pure Python Type"
    )
    assert proportion == 20
