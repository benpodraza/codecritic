def ping(user: str) -> str:
    return f"pong {user}"

# --- Agent Notes (linting / openai_gpt_4o_agent_engine) ---
# - Added type hints to the `ping` function to specify that `user` is a `str` and the function returns a `str`. This improves code readability and helps with static type checking using tools like `mypy`.
# - Removed unnecessary spaces around the parameter `user` to conform to PEP8 guidelines.
# - Ensured the code is formatted according to `black` standards by making sure the function definition and return statement are properly aligned.
# -----------------------------------------------