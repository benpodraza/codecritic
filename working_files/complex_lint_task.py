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
        log_message("Data saved to " + file_name)
    except Exception as e:
        log_message("Failed to save data: " + str(e), "ERROR")

def read_data_from_json(file_name: str) -> Optional[Dict[str, Any]]:
    try:
        with open(file_name) as f:
            return json.load(f)
    except Exception as e:
        log_message("Failed to read data: " + str(e), "ERROR")
        return None

def main() -> None:
    r = 5
    a = calculate_area(r)
    if a > 0:
        log_message("Area is: " + str(a))

    d = {"id": generate_uuid(), "name": "John", "age": 30}
    f = "data.json"
    save_data_to_json(d, f)
    loaded = read_data_from_json(f)
    log_message("Loaded: " + str(loaded))

if __name__ == "__main__":
    main()

# --- Agent Notes (PROVIDER_TYPE.SESSION / linting_generator_agent_provider) ---
# - Added type hints to all functions to comply with `mypy` requirements.
# - Separated import statements to conform to PEP8 guidelines.
# - Added exception handling in `read_data_from_json` to log the exception message, improving error transparency.
# - Ensured consistent return types in `calculate_area` by returning `0.0` instead of `0`.
# - These changes improve code readability and maintainability without altering the original logic.
# -----------------------------------------------
