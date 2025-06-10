def decision(x: int) -> str:
    if x > 0:
        return 'yes'
    elif x < 0:
        return 'no'
    else:
        return 'maybe'
# --- Agent Notes (linting / linting_generator_agent_provider) ---
# - Added type hints to the function `decision` to specify that it takes an integer and returns a string. This improves code clarity and helps with static type checking.
# - Formatted the code to conform to PEP8 guidelines by adding proper indentation and spacing.
# - Ensured that the code is valid and executable, addressing the Ruff parse error.
# - No significant tradeoffs were made; the changes are minimal and preserve the original logic and structure of the code.
# -----------------------------------------------
