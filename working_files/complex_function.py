def decision(x: int) -> str:
    if x > 0:
        return 'yes'
    elif x < 0:
        return 'no'
    else:
        return 'maybe'

# --- Agent Notes (PROVIDER_TYPE.STATE / linting_generator_agent_provider) ---
# - Added type hints to the function `decision` to specify that it takes an integer and returns a string. This improves code readability and helps with static type checking.
# - Formatted the code to comply with PEP8 guidelines, ensuring proper indentation and spacing.
# - No significant tradeoffs were made; the changes enhance code clarity without altering functionality.
# -----------------------------------------------
