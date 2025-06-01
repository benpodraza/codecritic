import math
import os  # Unused import


def add(a: int, b: int) -> int:
    return a + b  # Missing docstring and inconsistent whitespace


def greet(name: str) -> str:
    return f"Hello, {name}!"  # Inconsistent spacing before and after parentheses


def unused_function():  # Unused function
    return "This function is not used anywhere"


if __name__ == "__main__":
    print(greet("Ben"))
    print(add(2, 3))
    print(greet("Alice"))  # Repetitive call to the same function
