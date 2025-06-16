# Avoid shadowing the built-in 'list' by renaming the variable
numbers = [1, 2, 3]
print(numbers)

# --- Agent Notes (PROVIDER_TYPE.SESSION / linting_generator_agent_provider) ---
# - Renamed the variable `list` to `numbers` to avoid shadowing the built-in `list` type, which can lead to unexpected behavior and reduce code readability.
# - This change preserves the original intent and functionality of the code while improving its clarity and maintainability.
# -----------------------------------------------
