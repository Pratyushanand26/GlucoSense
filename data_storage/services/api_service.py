import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

def fetch_smartwatch_data():
    """
    Fetch health data from smartwatch API
    """
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()

        print("✅ Data fetched from API successfully!")
        return data

    except requests.exceptions.RequestException as e:
        print("❌ API fetch error:", e)
        return None
