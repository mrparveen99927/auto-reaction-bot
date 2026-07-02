# database.py - डेटाबेस हैंडलर फ़ाइल

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import config

# MongoDB से कनेक्शन स्थापित करना
client = AsyncIOMotorClient(config.MONGO_URI)
db = client[config.DB_NAME]
users_col = db[config.COLLECTION_NAME]

async def add_or_renew_user(vip_id, password, days):
    """एडमिन द्वारा नया यूजर बनाने या रिन्यू करने के लिए"""
    expiry_date = datetime.now() + timedelta(days=days)
    await users_col.update_one(
        {"vip_id": vip_id},
        {"$set": {
            "password": password,
            "expires_on": expiry_date,
            "status": "Active"
        }, "$setOnInsert": {
            "chat_id": None, # जब तक लॉगिन न हो, खाली रहेगा
            "telegram_user_id": None
        }},
        upsert=True
    )
    return expiry_date

async def ban_vip_user(vip_id):
    """यूजर को बैन करने के लिए"""
    res = await users_col.update_one({"vip_id": vip_id}, {"$set": {"status": "Banned"}})
    return res.modified_count > 0

async def get_vip_user(vip_id):
    """यूजर का डेटा निकालने के लिए"""
    return await users_col.find_one({"vip_id": vip_id})

async def check_chat_permission(chat_id):
    """रिएक्शन इंजन के लिए: चेक करता है कि चैनल एक्टिव है या नहीं"""
    user = await users_col.find_one({"chat_id": str(chat_id)})
    if user and user["status"] == "Active":
        if datetime.now() < user["expires_on"]:
            return True
    return False

async def lock_user_to_chat(vip_id, chat_id, telegram_user_id):
    """लॉगिन के वक्त वन-टाइम चैनल ID लॉक करने के लिए"""
    await users_col.update_one(
        {"vip_id": vip_id},
        {"$set": {"chat_id": str(chat_id), "telegram_user_id": telegram_user_id}}
    )

async def get_db_stats():
    """एड敏 के लिए स्टैट्स इकट्ठा करना"""
    total = await users_col.count_documents({})
    active = await users_col.count_documents({"status": "Active"})
    banned = await users_col.count_documents({"status": "Banned"})
    locked = await users_col.count_documents({"chat_id": {"$ne": None}})
    return total, active, banned, locked
    