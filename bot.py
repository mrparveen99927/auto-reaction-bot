# bot.py - 100% क्रैश फ्री अपडेटेड कोड

import os
import asyncio
import random
import threading
from datetime import datetime, timedelta
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient

# --- कॉन्फ़िगरेशन (CONFIGURATION) ---
BOT_TOKEN = "8843244865:AAGS47kvrD-ZeOTr-EgxSYFoYY-Cg3SJk-A"
ADMIN_ID = 1780858471
MONGO_URI = "mongodb+srv://arena_user:Arena999@cluster0.pluvfcd.mongodb.net/central_wallet_db?appName=Cluster0"

# Telegram API Credentials
API_ID = 123456
API_HASH = "your_api_hash_here"

# ⚠️ यहाँ अपने सभी 23 असली बॉट टोकन कॉमा (,) लगाकर डाल दें
HELPER_TOKENS = [
    "8843244865:AAGS47kvrD-ZeOTr-EgxSYFoYY-Cg3SJk-A", # उदाहरण के लिए पहला टोकन
    "TOKEN_BOT_2", "TOKEN_BOT_3", "TOKEN_BOT_4", "TOKEN_BOT_5",
    "TOKEN_BOT_6", "TOKEN_BOT_7", "TOKEN_BOT_8", "TOKEN_BOT_9", "TOKEN_BOT_10",
    "TOKEN_BOT_11", "TOKEN_BOT_12", "TOKEN_BOT_13", "TOKEN_BOT_14", "TOKEN_BOT_15",
    "TOKEN_BOT_16", "TOKEN_BOT_17", "TOKEN_BOT_18", "TOKEN_BOT_19", "TOKEN_BOT_20",
    "TOKEN_BOT_21", "TOKEN_BOT_22", "TOKEN_BOT_23"
]

# ऑटोमैटिक रिएक्शंस की लिस्ट जो रैंडमली पोस्ट पर जाएगी
REACTIONS_POOL = ["👍", "🔥", "❤️", "🥰", "👏", "🎉", "🤩", "🚀", "⚡"]

# 23 हेल्पर बॉट्स के यूजरनेम की लिस्ट जो ग्राहकों को लॉगिन के बाद दिखेगी
BOT_LIST_TEXT = """
@FastReact1_bot   | @FastReact2_bot   | @FastReact3_bot
@FastReact4_bot   | @FastReact5_bot   | @FastReact6_bot
@FastReact7_bot   | @FastReact8_bot   | @FastReact9_bot
@FastReact10_bot  | @FastReact11_bot  | @FastReact12_bot
@FastReact13_bot  | @FastReact14_bot  | @FastReact15_bot
@FastReact16_bot  | @FastReact17_bot  | @FastReact18_bot
@FastReact19_bot  | @FastReact20_bot  | @FastReact21_bot
@FastReact22_bot  | @FastReact23_bot
"""

# --- DATABASE SETUP ---
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["reaction_bot_db"]
users_col = db["reaction_vip_users"]

# --- MAIN CONTROL BOT CLIENT ---
main_bot = Client("MainBotEngine", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- FLASK SERVER (Render को लाइव रखने के लिए पोर्ट बाइंडिंग) ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home(): 
    return "✅ Central Reaction Bot Server is Live and Healthy!", 200

@flask_app.route('/telegram', methods=['POST'])
def webhook(): 
    return "OK", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# ==================== 👑 ADMIN COMMANDS ====================

@main_bot.on_message(filters.command("gen") & filters.user(ADMIN_ID))
async def gen_cmd(_, message: Message):
    args = message.command
    if len(args) < 4:
        await message.reply_text("❌ FORMAT: `/gen [id] [password] [days]`")
        return
    vip_id = args[1]
    password = args[2]
    days = int(args[3])
    expiry = datetime.now() + timedelta(days=days)
    
    await users_col.update_one(
        {"vip_id": vip_id},
        {"$set": {
            "password": password, 
            "expires_on": expiry, 
            "status": "Active"
        }, "$setOnInsert": {
            "chat_id": None,
            "telegram_user_id": None
        }},
        upsert=True
    )
    await message.reply_text(f"✅ **VIP Account Created!**\n\n🔑 ID: `{vip_id}`\n🔒 Pass: `{password}`\n⏳ Valid for: {days} Days\n📅 Expires On: {expiry.strftime('%Y-%m-%d')}")

@main_bot.on_message(filters.command("ban") & filters.user(ADMIN_ID))
async def ban_cmd(_, message: Message):
    args = message.command
    if len(args) < 2:
        await message.reply_text("❌ FORMAT: `/ban [vip_id]`")
        return
    vip_id = args[1]
    res = await users_col.update_one({"vip_id": vip_id}, {"$set": {"status": "Banned"}})
    if res.modified_count > 0:
        await message.reply_text(f"🚫 VIP ID `{vip_id}` को बैन कर दिया गया है।")
    else:
        await message.reply_text("❌ आईडी नहीं मिली।")

@main_bot.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats_cmd(_, message: Message):
    total = await users_col.count_documents({})
    active = await users_col.count_documents({"status": "Active"})
    locked = await users_col.count_documents({"chat_id": {"$ne": None}})
    await message.reply_text(f"📊 **Reaction Bot Live Stats:**\n\n👥 कुल VIP आईडी: {total}\n🟢 एक्टिव यूज़र्स: {active}\n🔒 लॉक्ड चैनल/ग्रुप्स: {locked}")

# ==================== 👤 USER COMMANDS ====================

@main_bot.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message: Message):
    await message.reply_text("👋 **VIP 23x Reaction Bot में आपका स्वागत है!**\n\nलॉगिन करने के लिए कृपया इस फॉर्मेट का उपयोग करें:\n`/login [vip_id] [password] [@your_channel_username]`")

@main_bot.on_message(filters.command("login") & filters.private)
async def login_cmd(_, message: Message):
    args = message.command
    if len(args) < 4:
        await message.reply_text("❌ FORMAT: `/login [vip_id] [password] [@channel]`")
        return
    vip_id = args[1]
    password = args[2]
    target_chat = args[3]
    
    account = await users_col.find_one({"vip_id": vip_id})
    if not account or account["password"] != password:
        await message.reply_text("❌ गलत VIP ID या पासवर्ड।")
        return
    if account["status"] == "Banned":
        await message.reply_text("🚫 आपका अकाउंट बैन कर दिया गया है!")
        return
    if datetime.now() > account["expires_on"]:
        await message.reply_text("⏳ आपका प्रीमियम प्लान समाप्त (Expire) हो चुका है!")
        return

    try:
        chat_info = await main_bot.get_chat(target_chat)
        chat_id = str(chat_info.id)
    except Exception:
        await message.reply_text("❌ बॉट आपके चैनल को ढूंढ नहीं पाया। सुनिश्चित करें कि चैनल पब्लिक है या बॉट उसमें मौजूद है।")
        return

    if account.get("chat_id") and account["chat_id"] != chat_id:
        await message.reply_text(f"❌ सुरक्षा नियम: यह VIP ID पहले से ही किसी अन्य चैट ID (`{account['chat_id']}`) पर लॉक है!")
        return

    await users_col.update_one(
        {"vip_id": vip_id}, 
        {"$set": {"chat_id": chat_id, "telegram_user_id": message.from_user.id}}
    )
    
    dashboard = f"""
✅ **Login Successful!**

🔑 **VIP ID:** {vip_id}
📅 **Expires On:** {account['expires_on'].strftime('%Y-%m-%d')}
🔒 **Status:** Locked to Chat ID: `{chat_id}`

🤖 **VIP Helper Bots List (Touch to Copy):**
{BOT_LIST_TEXT}

ℹ️ *इन सभी बॉट्स को अपने चैनल में एडमिन बनाएं। रिएक्शंस ऑटोमैटिक शुरू हो जाएंगे!*
"""
    await message.reply_text(dashboard)

# ==================== 🤖 AUTO REACTION LOGIC ====================

@main_bot.on_message(filters.chat & ~filters.service)
async def reaction_handler(_, message: Message):
    chat_id = str(message.chat.id)
    
    # चेक करें कि क्या यह चैनल किसी एक्टिव VIP कस्टमर का है
    allowed = await users_col.find_one({"chat_id": chat_id, "status": "Active"})
    if not allowed or datetime.now() > allowed["expires_on"]:
        return

    print(f"✨ VIP Channel Post Detected in {chat_id}. Discharging 23x reactions...")

    # सभी 23 बॉट्स से बारी-बारी रिएक्शन दिलवाना (0.2 सेकंड के गैप पर)
    for index, token in enumerate(HELPER_TOKENS):
        if token.startswith("TOKEN_"): # नकली टोकन को स्किप करने के लिए
            continue
        try:
            async with Client(f"worker_{index}", api_id=API_ID, api_hash=API_HASH, bot_token=token) as worker:
                chosen_reaction = random.choice(REACTIONS_POOL)
                await worker.send_reaction(chat_id=message.chat.id, message_id=message.id, values=chosen_reaction)
                await asyncio.sleep(0.2) # एंटी-स्पैम डिले
        except Exception as e:
            print(f"Bot {index+1} Failed: {e}")
            continue

# --- STARTUP LOGIC ---
async def start_all():
    # Flask को बैकग्राउंड थ्रेड में चलाना
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🤖 Main Control Bot Starting...")
    await main_bot.start()
    print("🚀 Bot Business System is fully ONLINE!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_all())
    