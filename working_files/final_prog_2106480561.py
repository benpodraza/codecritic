def ping(user: str) -> str:
    return f"pong {user}"

# --- Agent Notes (linting / openai_gpt_4o_agent_engine) ---
# - Added type hints to the `ping` function to specify that `user` is a `str` and the function returns a `str`. This improves code readability and helps with static type checking.
# - Removed unnecessary space between `ping` and `user` in the function definition to conform to PEP8 guidelines.
# - Ensured the function remains valid and executable with minimal changes to preserve the original intent.
# -----------------------------------------------