# reaction_engine.py
import random
import asyncio
import httpx
import logging
from telegram import Update
from config import HELPER_BOTS
from database import users_collection

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

async def send_reaction_direct(token, chat_id, message_id, reaction):
    url = f"https://telegram.org{token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": reaction}],
        "is_big": True
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=5.0)
            res_json = response.json()
            if not res_json.get("ok"):
                logging.error(f"❌ Telegram API Error for Token ...{token[-8:]}: {res_json.get('description')}")
            else:
                logging.info(f"✅ Reaction Success for Token ...{token[-8:]}")
    except Exception as e:
        logging.error(f"⚠️ HTTP Connection Error: {str(e)}")

async def auto_react(update: Update, context):
    # 1. ग्रुप मैसेज या चैनल पोस्ट दोनों को कैप्चर करना
    target_msg = update.message or update.channel_post
    if not target_msg: return
    
    group_id = update.effective_chat.id
    
    # 2. फिक्स: मोंगोडीबी कलेक्शन से सीधे लाइव चेक करना बिना किसी बाहरी फ़ंक्शन के झंझट के
    user = await users_collection.find_one({"group_id": group_id, "status": "active"})
    if not user:
        logging.warning(f"⚠️ Reaction blocked: Chat ID {group_id} is not activated in Database!")
        return
        
    # 3. प्रीमियम रिएक्शंस लिस्ट
    premium_reactions = ["👍", "❤", "🔥", "🎉", "🤩", "🚀", "🥰", "👏", "⚡", "😎"]
    
    # 4. 23 बोट्स से पैरेलल ब्लास्ट चालू करना
    tasks = [
        send_reaction_direct(bot["token"], group_id, target_msg.message_id, random.choice(premium_reactions))
        for bot in HELPER_BOTS
    ]
    await asyncio.gather(*tasks)
    