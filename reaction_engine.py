# reaction_engine.py
import random
import asyncio
import httpx
from telegram import Update
from config import HELPER_BOTS
from database import is_group_allowed

async def send_reaction_direct(token, chat_id, message_id, reaction):
    # बिना बोट चालू किए सीधे टेलीग्राम एंडपॉइंट पर हिट करना
    url = f"https://telegram.org{token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": reaction}],
        "is_big": True
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, timeout=5.0)
    except:
        pass

async def auto_react(update: Update, context):
    target_msg = update.message or update.channel_post
    if not target_msg: return
    
    group_id = update.effective_chat.id
    if not await is_group_allowed(group_id): return
    
    premium_reactions = ["👍", "❤", "🔥", "🎉", "🤩", "🚀", "🥰", "👏", "⚡", "😎"]
    
    # 23 बोट्स से बिना वेबहुक क्रैश के पैरेलल (Parallel) रिक्वेस्ट ब्लास्ट करना
    tasks = [
        send_reaction_direct(bot["token"], group_id, target_msg.message_id, random.choice(premium_reactions))
        for bot in HELPER_BOTS
    ]
    await asyncio.gather(*tasks)
    