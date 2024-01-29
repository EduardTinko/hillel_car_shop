import json
import os


data = os.getenv("GOOGLE_STORAGE_KEYS")

if data:
    try:
        json_data = json.loads(data)
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
    else:
        with open("google_storage.json", "w") as json_file:
            json.dump(json_data, json_file, indent=None)
