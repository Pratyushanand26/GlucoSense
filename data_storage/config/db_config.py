from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

def get_db_connection():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        print("✅ MongoDB connection successful!")
        return db
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
        raise
