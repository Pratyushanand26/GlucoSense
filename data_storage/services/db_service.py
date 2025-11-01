from config.db_config import get_db_connection
import os
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")

def insert_health_data(data):
    """
    Inserts smartwatch health data into MongoDB collection
    """
    db = get_db_connection()
    collection = db[COLLECTION_NAME]

    if not data:
        print("⚠️ No data to insert.")
        return

    # If data is a list of records
    if isinstance(data, list):
        result = collection.insert_many(data)
        print(f"✅ Inserted {len(result.inserted_ids)} records into MongoDB.")
    else:
        result = collection.insert_one(data)
        print(f"✅ Inserted 1 record with id: {result.inserted_id}")
