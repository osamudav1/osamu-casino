import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://Osamu:308240db@cluster0.eephj6y.mongodb.net/?appName=Cluster0")
DB_NAME = os.getenv("MONGO_DB_NAME", "casino")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "users")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
users_collection = db[COLLECTION_NAME]

async def get_user_balance(user_id: int, default_points: int = 50) -> int:
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        # Check alternative field names like id or _id if common
        user = await users_collection.find_one({"_id": user_id})
    
    if user and "balance" in user:
        return int(user["balance"])
    elif user and "$" in user:
        return int(user["$"])
    
    # If user doesn't exist, create with starting balance
    await users_collection.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"balance": default_points}},
        upsert=True
    )
    return default_points

async def update_user_balance(user_id: int, new_balance: int):
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"balance": new_balance}},
        upsert=True
    )
