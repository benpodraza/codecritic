def ping(user: str) -> str:
    return f"pong {user}"

# --- Agent Notes (linting / openai_gpt_4o_agent_engine) ---
# - Added type hints to the `ping` function to specify that `user` is a `str` and the function returns a `str`. This improves code readability and helps with type checking.
# - Removed the space between the function name and the parameter list to conform to PEP8 guidelines.
# - Ensured the code is formatted according to `black` standards, which typically involves consistent spacing and line breaks.
# -----------------------------------------------