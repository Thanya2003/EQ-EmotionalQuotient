import json

try:
    with open('questions_above_18.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("JSON loaded successfully!")
except Exception as e:
    print(f"Error loading JSON: {e}")
