def decision(x: int) -> str:
    if x > 0:
        return 'yes'
    elif x < 0:
        return 'no'
    else:
        return 'maybe'

# --- Agent Notes (PROVIDER_TYPE.SESSION / linting_generator_agent_provider) ---
# - Added type hints to the function `decision` to specify that it takes an integer and returns a string. This enhances code readability and helps with static type checking.
# - Formatted the code to conform to PEP8 guidelines by adding proper indentation and spaces around operators.
# - No tradeoffs were made; these changes improve code quality and maintainability without altering functionality.
# -----------------------------------------------
