import sys
import os


def add(a: int, b: int) -> int:
    result = a + b
    return result


class MyClass:
    def __init__(self, value: int):
        self.value = value

    def print_value(self) -> None:
        print(self.value)


add(1, 2)
