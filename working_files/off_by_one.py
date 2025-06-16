def inclusive_range(n: int) -> list:
    return list(range(n + 1))  # Corrected to include n in the range

# --- Agent Notes (PROVIDER_TYPE.SESSION / linting_generator_agent_provider) ---
# - Added type hints to the function `inclusive_range` to specify that it takes an integer and returns a list. This enhances code readability and helps with static type checking.
# - Corrected the range function to `range(n + 1)` to ensure the range is inclusive of `n`, as suggested by the comment in the original code.
# - No tradeoffs were made; the change maintains the original intent and functionality of the code.
# -----------------------------------------------
