import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://Osamu:308240db@cluster0.eephj6y.mongodb.net/?appName=Cluster0")
DB_NAME = os.getenv("MONGO_DB_NAME", "casino")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "users")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
users_collection = db[COLLECTION_NAME]

async def get_user_balance(user_id: int, default_points: int = 50) -> int:
    # Search by user_id or id or telegram id fields
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        user = await users_collection.find_one({"id": user_id})
    if not user:
        user = await users_collection.find_one({"_id": user_id})
    
    if user:
        if "$" in user:
            return int(user["$"])
        elif "balance" in user:
            return int(user["balance"])
    
    # If user doesn't exist, create with starting balance in '$'
    await users_collection.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"$": default_points}},
        upsert=True
    )
    return default_points

async def update_user_balance(user_id: int, new_balance: int):
    # Update '$' field in MongoDB
    result = await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"$": new_balance}}
    )
    if result.matched_count == 0:
        result = await users_collection.update_one(
            {"id": user_id},
            {"$set": {"$": new_balance}}
        )
    if result.matched_count == 0:
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"$": new_balance}},
            upsert=True
        )
