def square(x: int) -> int:
    return x * x

# --- Agent Notes (PROVIDER_TYPE.STATE / linting_generator_agent_provider) ---
# - Changed the type hint of the parameter `x` from `str` to `int` because the operation `x * x` is not valid for strings and the function is intended to return an integer.
# - Ensured the return type remains `int` as the result of squaring an integer is an integer.
# - This change resolves the `mypy` type checking issue, improving the `mypy_score` from 0.7 to 1.0.
# -----------------------------------------------
