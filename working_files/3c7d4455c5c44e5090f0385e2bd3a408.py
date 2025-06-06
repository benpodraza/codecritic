def ping(user: str) -> str:
    return f"pong {user}"

# --- Agent Notes (linting / openai_gpt_4o_agent_engine) ---
# - Added type hints to the `ping` function to specify that `user` should be a string and the function returns a string. This improves code readability and helps with type checking.
# - Removed unnecessary spaces around the parameter `user` in the function definition to conform to PEP8 guidelines.
# - Ensured the function remains simple and retains its original intent.
# -----------------------------------------------