def square(x: int) -> int:
    return x * x

# --- Agent Notes (PROVIDER_TYPE.SESSION / linting_generator_agent_provider) ---
# - Changed the type hint of the parameter `x` from `str` to `int` because the operation `x * x` is valid for integers, not strings.
# - Ensured the return type remains `int` as the result of squaring an integer is an integer.
# - This change resolves the `mypy` type-checking issue, improving the `mypy_score`.
# - No tradeoffs were made as the original intent of the function was preserved.
# -----------------------------------------------
