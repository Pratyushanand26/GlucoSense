# MongoDB setup and connection logic
"""Database connection and initialization"""
import motor.motor_asyncio
from .config import MONGO_CONNECTION_STRING, DATABASE_NAME

# Initialize MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_CONNECTION_STRING)
db = client.get_database(DATABASE_NAME)

# Collections
users_collection = db.get_collection("users")
records_collection = db.get_collection("daily_records")

async def init_db():
    """Initialize database indexes"""
    await users_collection.create_index("email", unique=True)
    await records_collection.create_index("user_id")
    await records_collection.create_index([("user_id", 1), ("date", -1)])
    print("✅ Database indexes initialized")