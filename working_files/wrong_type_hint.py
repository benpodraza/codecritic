def square(x: int) -> int:
    return x * x
# --- Agent Notes (linting / linting_generator_agent_provider) ---
# - Changed the parameter type hint from `str` to `int` in the function `square` to match the intended operation of squaring a number, which requires numerical input.
# - Ensured the return type hint remains as `int` since the result of squaring an integer is also an integer.
# - This change resolves the Ruff parse error and aligns the function's implementation with its intended purpose.
# - No significant tradeoffs were made; the changes are minimal and maintain the original intent of the code.
# -----------------------------------------------
