import json
import uuid
from datetime import datetime

def generate_uuid() -> str:
    """Generates a unique identifier."""
    return str(uuid.uuid4())

def log_message(message: str, log_level: str = "INFO") -> None:
    """Logs a message with a specified log level."""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] [{log_level}] {message}")

def calculate_area(radius: float) -> float:
    """Calculates the area of a circle."""
    if radius <= 0:
        log_message("Invalid radius value. Must be greater than zero.", "ERROR")
        return 0.0
    return 3.14159 * (radius ** 2)

def save_data_to_json(data: dict, file_name: str) -> None:
    """Saves data as a JSON file."""
    try:
        with open(file_name, "w") as f:
            json.dump(data, f, indent=4)
        log_message(f"Data saved to {file_name}")
    except Exception as e:
        log_message(f"Failed to save data: {str(e)}", "ERROR")

def read_data_from_json(file_name: str) -> dict:
    """Reads data from a JSON file."""
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except Exception as e:
        log_message(f"Failed to read data: {str(e)}", "ERROR")
        return {}

def main():
    radius = 5
    area = calculate_area(radius)
    if area > 0:
        log_message(f"Area of circle with radius {radius} is {area:.2f}")
    
    # Save and read example data
    data = {"id": generate_uuid(), "name": "John Doe", "age": 30}
    file_name = "data.json"
    save_data_to_json(data, file_name)
    loaded_data = read_data_from_json(file_name)
    log_message(f"Loaded data: {loaded_data}")

if __name__ == "__main__":
    main()
