def decision(x: int) -> str:
    if x > 0:
        return 'yes'
    elif x < 0:
        return 'no'
    else:
        return 'maybe'

# --- Agent Notes (PROVIDER_TYPE.SESSION / linting_generator_agent_provider) ---
# - Added type hints to the function `decision` to specify that `x` is an `int` and the return type is `str`. This improves code clarity and helps with static type checking.
# - Reformatted the code to conform to PEP8 guidelines, ensuring proper indentation and spacing around operators.
# - No significant tradeoffs were made; the changes enhance readability and maintainability without altering the original logic.
# -----------------------------------------------
