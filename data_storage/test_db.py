import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

sample_data = {
    "user_id": "demo123",
    "heart_rate": 75,
    "steps": 4000
}

result = collection.insert_one(sample_data)
print("✅ Inserted document with _id:", result.inserted_id)
