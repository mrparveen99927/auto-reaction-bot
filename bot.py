# bot.py - कंबाइंड ऑल-इन-वन 100% वर्किंग कोड

import os
import asyncio
import random
import threading
from datetime import datetime, timedelta
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient

# --- कॉन्फ़िगरेशन ---
BOT_TOKEN = "8843244865:AAGS47kvrD-ZeOTr-EgxSYFoYY-Cg3SJk-A"
ADMIN_ID = 1780858471  # सुनिश्चित करें कि आपकी आईडी यही है
MONGO_URI = "mongodb+srv://arena_user:Arena999@cluster0.pluvfcd.mongodb.net/central_wallet_db?appName=Cluster0"

API_ID = 123456
API_HASH = "your_api_hash_here"

# 23 हेल्पर्स बॉट टोकन्स (यहाँ अपने असली टोकन डालें)
HELPER_TOKENS = [
    "TOKEN_1", "TOKEN_2", "TOKEN_3", "TOKEN_4", "TOKEN_5",
    "TOKEN_6", "TOKEN_7", "TOKEN_8", "TOKEN_9", "TOKEN_10",
    "TOKEN_11", "TOKEN_12", "TOKEN_13", "TOKEN_14", "TOKEN_15",
    "TOKEN_16", "TOKEN_17", "TOKEN_18", "TOKEN_19", "TOKEN_20",
    "TOKEN_21", "TOKEN_22", "TOKEN_23"
]

REACTIONS_POOL = ["👍", "🔥", "❤️", "🥰", "👏", "🎉", "🤩", "🚀", "⚡"]

# --- डेटाबेस कनेक्शन ---
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["reaction_bot_db"]
users_col = db["reaction_vip_users"]

# --- मेन बॉट क्लाइंट ---
main_bot = Client("MainBotEngine", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- हेल्पर्स मास्टर क्लाइंट ---
master_worker = Client("MasterWorkerEngine", api_id=API_ID, api_hash=API_HASH, bot_token=HELPER_TOKENS[0])

# --- FLASK WEB SERVER ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home(): return "Live", 200

@flask_app.route('/telegram', methods=['POST'])
def webhook(): return "OK", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# ==================== ADMIN COMMANDS ====================

@main_bot.on_message(filters.command("gen") & filters.user(ADMIN_ID))
async def gen_cmd(_, message: Message):
    args = message.command
    if len(args) < 4:
        await message.reply_text("❌ फॉर्मेट: `/gen [id] [password] [days]`")
        return
    vip_id, password, days = args[1], args[2], int(args[3])
    expiry = datetime.now() + timedelta(days=days)
    
    await users_col.update_one(
        {"vip_id": vip_id},
        {"$set": {"password": password, "expires_on": expiry, "status": "Active"}},
        upsert=True
    )
    await message.reply_text(f"✅ **VIP Created!**\n🔑 ID: `{vip_id}`\n🔒 Pass: `{password}`\n⏳ Days: {days}")

@main_bot.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats_cmd(_, message: Message):
    total = await users_col.count_documents({})
    active = await users_col.count_documents({"status": "Active"})
    locked = await users_col.count_documents({"chat_id": {"$ne": None}})
    await message.reply_text(f"📊 **Stats:**\nTotal Keys: {total}\nActive: {active}\nLocked: {locked}")

# ==================== USER COMMANDS ====================

@main_bot.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message: Message):
    await message.reply_text("👋 लॉगिन करने के लिए टाइप करें:\n`/login [vip_id] [password] [@channel]`")

@main_bot.on_message(filters.command("login") & filters.private)
async def login_cmd(_, message: Message):
    args = message.command
    if len(args) < 4:
        await message.reply_text("❌ फॉर्मेट: `/login [vip_id] [password] [@channel]`")
        return
    vip_id, password, target_chat = args[1], args[2], args[3]
    
    account = await users_col.find_one({"vip_id": vip_id})
    if not account or account["password"] != password or account["status"] != "Active" or datetime.now() > account["expires_on"]:
        await message.reply_text("❌ आईडी गलत है या प्रीमियम खत्म हो चुका है।")
        return

    try:
        chat_info = await main_bot.get_chat(target_chat)
        chat_id = str(chat_info.id)
    except Exception:
        await message.reply_text("❌ बॉट चैनल को ढूंढ नहीं पाया।")
        return

    if account.get("chat_id") and account["chat_id"] != chat_id:
        await message.reply_text("❌ यह VIP ID पहले से किसी अन्य चैनल पर लॉक है!")
        return

    await users_col.update_one({"vip_id": vip_id}, {"$set": {"chat_id": chat_id}})
    await message.reply_text(f"✅ **Login Success!**\nLocked to Chat ID: `{chat_id}`\n\nअपने 23 बॉट्स को एडमिन बना दें!")

# ==================== AUTO REACTION LOGIC ====================

@master_worker.on_message(filters.chat() & ~filters.service)
async def reaction_handler(_, message: Message):
    chat_id = str(message.chat.id)
    allowed = await users_col.find_one({"chat_id": chat_id, "status": "Active"})
    
    if not allowed or datetime.now() > allowed["expires_on"]:
        return

    for index, token in enumerate(HELPER_TOKENS):
        try:
            async with Client(f"worker_{index}", api_id=API_ID, api_hash=API_HASH, bot_token=token) as worker:
                chosen = random.choice(REACTIONS_POOL)
                await worker.send_reaction(chat_id=message.chat.id, message_id=message.id, values=chosen)
                await asyncio.sleep(0.2)
        except Exception:
            continue

# --- STARTUP LOGIC ---
async def start_all():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    await main_bot.start()
    await master_worker.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_all())
    