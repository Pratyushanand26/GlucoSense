import json

def get_user_data():
    data = {
        "name": "Adi",
        "age": 20,
        "interests": ["AI", "Finance", "Cybersecurity"]
    }
    return json.dumps(data)
