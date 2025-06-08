def ping(user: str) -> str:
    return f"pong {user}"

# --- Agent Notes (linting / openai_gpt_4o_agent_engine) ---
# - Added type hints to the `ping` function to specify that `user` should be a string and the function returns a string. This improves code readability and helps with static type checking using `mypy`.
# - Removed the space between `ping(` and `user)` to conform to PEP8 guidelines regarding function definitions.
# - Ensured the code is formatted according to `black` standards by adjusting spacing and alignment.
# - These changes improve the code's compliance with PEP8 and enhance its readability without altering its functionality.
# -----------------------------------------------