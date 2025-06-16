def inclusive_range(n: int) -> list:
    return list(range(n + 1))  # corrected to include n

# --- Agent Notes (PROVIDER_TYPE.SESSION / linting_generator_agent_provider) ---
# - Changed `range(n)` to `range(n + 1)` to make the function inclusive of `n`, as indicated by the comment.
# - Added type hints to the function signature for better clarity and to improve `mypy` score.
# - No tradeoffs were made; the change aligns with the intended functionality described in the comment.
# -----------------------------------------------
