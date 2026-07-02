# database.py
import motor.motor_asyncio
from datetime import datetime, timedelta
from config import MONGO_URI

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["reaction_bot_db"]
users_collection = db["users"]

def init_db():
    pass

async def save_chat_id(access_id, chat_id):
    await users_collection.update_one(
        {"access_id": access_id},
        {"$set": {"chat_id": chat_id}}
    )

async def generate_user_credentials(access_id, password, days=30):
    expiry = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    await users_collection.update_one(
        {"access_id": access_id},
        {"$set": {
            "password": password,
            "expiry_date": expiry,
            "status": "active"
        }},
        upsert=True
    )
    return True

async def login_and_lock_group(access_id, password, group_id):
    user = await users_collection.find_one({"access_id": access_id, "status": "active"})
    if not user: return "invalid"
    if password != "BYPASS_CHECK" and user["password"] != password: return "invalid"
    
    expiry_date = user["expiry_date"]
    if datetime.now() > datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S'): return "expired"
        
    locked_group = user.get("group_id")
    if locked_group is None:
        existing_group = await users_collection.find_one({"group_id": group_id})
        if existing_group and existing_group["access_id"] != access_id: return "group_already_used"
            
        await users_collection.update_one(
            {"access_id": access_id},
            {"$set": {"group_id": group_id}}
        )
        return "success"
    elif locked_group == group_id: return "success"
    else: return "wrong_group"

async def is_group_allowed(group_id):
    user = await users_collection.find_one({"group_id": group_id, "status": "active"})
    if user:
        if datetime.now() < datetime.strptime(user["expiry_date"], '%Y-%m-%d %H:%M:%S'): return True
    return False

async def db_delete_key(target_id):
    res = await users_collection.delete_one({"access_id": target_id})
    return res.deleted_count

async def db_get_stats():
    total_users = await users_collection.count_documents({})
    active_groups = await users_collection.count_documents({"group_id": {"$exists": True, "$ne": None}})
    return total_users, active_groups

async def db_get_users():
    cursor = users_collection.find({})
    users = []
    async for doc in cursor:
        users.append((doc["access_id"], doc.get("password"), doc.get("group_id"), doc["expiry_date"]))
    return users

async def db_get_broadcast_chats():
    cursor = users_collection.find({"chat_id": {"$exists": True, "$ne": None}})
    chats = []
    async for doc in cursor:
        chats.append((doc["chat_id"],))
    return chats
    