import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

def generate_uuid() -> str:
    return str(uuid.uuid4())

def log_message(message: str, log_level: str = "INFO") -> None:
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] [{log_level}] {message}")

def calculate_area(radius: float) -> float:
    if radius <= 0:
        log_message("Invalid radius value. Must be greater than zero.", "ERROR")
        return 0.0
    return 3.14159 * radius ** 2

def save_data_to_json(data: Dict[str, Any], file_name: str) -> None:
    try:
        with open(file_name, "w") as f:
            json.dump(data, f)
        log_message(f"Data saved to {file_name}")
    except Exception as e:
        log_message(f"Failed to save data: {e}", "ERROR")

def read_data_from_json(file_name: str) -> Optional[Dict[str, Any]]:
    try:
        with open(file_name) as f:
            return json.load(f)
    except Exception as e:
        log_message(f"Failed to read data: {e}", "ERROR")
        return None

def main() -> None:
    r = 5
    a = calculate_area(r)
    if a > 0:
        log_message(f"Area is: {a}")

    d = {"id": generate_uuid(), "name": "John", "age": 30}
    f = "data.json"
    save_data_to_json(d, f)
    loaded = read_data_from_json(f)
    log_message(f"Loaded: {loaded}")

if __name__ == "__main__":
    main()

# --- Agent Notes (linting / linting_generator_agent_provider) ---
# - Split the import statement into separate lines for `json` and `uuid` to conform to PEP8 guidelines.
# - Added type hints to all functions to improve code clarity and enable type checking with `mypy`.
# - Changed the return type of `calculate_area` to `float` to ensure consistency in return type.
# - Updated the `read_data_from_json` function to catch exceptions and log the error message for better debugging.
# - Used f-strings for string formatting in `log_message` and `save_data_to_json` for improved readability.
# - Added exception handling in `read_data_from_json` to log the specific error message.
# - Ensured all functions have a return type of `None` where applicable to indicate they do not return a value.
# - These changes improve code readability, maintainability, and error handling without altering the original logic.
# -----------------------------------------------