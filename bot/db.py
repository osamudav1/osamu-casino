import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://Osamu:308240db@cluster0.eephj6y.mongodb.net/?appName=Cluster0")
DB_NAME = os.getenv("MONGO_DB_NAME", "casino")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "users")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
users_collection = db[COLLECTION_NAME]

async def get_user_balance(user_id: int, default_points: int = 50) -> int:
    uid_int = int(user_id)
    uid_str = str(user_id)
    
    # Try finding by user_id, id, or _id in various types
    user = await users_collection.find_one({
        "$or": [
            {"user_id": uid_int},
            {"user_id": uid_str},
            {"id": uid_int},
            {"id": uid_str},
            {"_id": uid_int},
            {"_id": uid_str},
        ]
    })
    
    if user:
        logger.info(f"Found user in MongoDB for {user_id}: {user}")
        if "$" in user and user["$"] is not None:
            try:
                return int(user["$"])
            except (ValueError, TypeError):
                pass
        if "balance" in user and user["balance"] is not None:
            try:
                return int(user["balance"])
            except (ValueError, TypeError):
                pass
    
    # If user not found, insert with user_id as int and '$' as default_points
    logger.info(f"User {user_id} not found in MongoDB, creating with default balance {default_points}")
    await users_collection.update_one(
        {"user_id": uid_int},
        {"$setOnInsert": {"$": default_points}},
        upsert=True
    )
    return default_points

async def update_user_balance(user_id: int, new_balance: int):
    uid_int = int(user_id)
    uid_str = str(user_id)
    
    # Try updating existing document matching user_id or id
    result = await users_collection.update_one(
        {
            "$or": [
                {"user_id": uid_int},
                {"user_id": uid_str},
                {"id": uid_int},
                {"id": uid_str},
            ]
        },
        {"$set": {"$": new_balance}}
    )
    
    if result.matched_count == 0:
        # Upsert if not found
        await users_collection.update_one(
            {"user_id": uid_int},
            {"$set": {"$": new_balance}},
            upsert=True
        )
    logger.info(f"Updated balance for user {user_id} to {new_balance}")
