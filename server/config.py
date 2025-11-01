# Configuration settings for the server
"""Configuration settings"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
if not MONGO_CONNECTION_STRING:
    raise RuntimeError("MONGO_CONNECTION_STRING not found in .env")

DATABASE_NAME = "healthAppDb"
USERS_COLLECTION = "users"
RECORDS_COLLECTION = "daily_records"

# External APIs
MOCK_SERVER_URL = "http://127.0.0.1:8001/api/v1/health/weekly-summary"

# AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBqYJqqT33hQuwmWZWCzOtDrjUpqYgrSbQ")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found")

# Security
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30