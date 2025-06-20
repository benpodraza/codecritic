import json, uuid
from datetime import datetime

def generate_uuid():
    return str(uuid.uuid4())

def log_message(message, log_level = "INFO"):
  timestamp=datetime.now().isoformat()
  print(f"[{timestamp}] [{log_level}] {message}")

def calculate_area(radius):
    if radius <= 0:
      log_message("Invalid radius value. Must be greater than zero.", "ERROR")
      return 0
    return 3.14159 * radius ** 2

def save_data_to_json(data, file_name):
    try:
      with open(file_name, "w") as f:
          json.dump(data, f)
      log_message("Data saved to " + file_name)
    except Exception as e:
      log_message("Failed to save data: " + str(e), "ERROR")

def read_data_from_json(file_name):
    try:
        with open(file_name) as f:
            return json.load(f)
    except:
        log_message("Failed to read data", "ERROR")
        return None

def main():
    r = 5
    a = calculate_area(r)
    if a > 0: log_message("Area is: " + str(a))

    d = {"id": generate_uuid(),"name":"John","age":30}
    f = "data.json"
    save_data_to_json(d, f)
    loaded = read_data_from_json(f)
    log_message("Loaded: " + str(loaded))

if __name__=="__main__": main()
