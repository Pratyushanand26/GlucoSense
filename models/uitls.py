import re
import json

def extract_json_from_text(text: str):
    """
    Extracts and parses a JSON object from a string.
    Handles model outputs that include explanations, markdown, or extra text.

    Args:
        text (str): The raw string (e.g., from a model response).

    Returns:
        dict: Parsed JSON object if valid.
        None: If no valid JSON object was found.
    """
    if not text or not isinstance(text, str):
        print("⚠️ Invalid input: expected non-empty string.")
        return None

    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            json_data = json.loads(match.group(0))
            return json_data
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON decoding failed: {e}")
            return None
    else:
        print("⚠️ No valid JSON found in text.")
        return None
