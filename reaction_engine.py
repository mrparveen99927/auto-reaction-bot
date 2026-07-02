# reaction_engine.py
import random
import httpx
import asyncio
from telegram import Update
from config import HELPER_BOTS
from database import is_group_allowed

async def send_reaction_async(client, token, chat_id, message_id, reaction):
    try:
        url = f"https://telegram.org{token}/setMessageReaction"
        data = {
            "chat_id": chat_id, 
            "message_id": message_id, 
            "reaction": [{"type": "emoji", "emoji": reaction}], 
            "is_big": True
        }
        await client.post(url, json=data, timeout=5)
    except Exception:
        pass

async def auto_react(update: Update, context):
    if not update.message:
        return
    group_id = update.effective_chat.id
    if not is_group_allowed(group_id):
        return

    message_id = update.message.message_id
    premium_reactions = ["👍", "❤️", "🔥", "🎉", "🤩", "🚀", "🥰", "👏", "⚡️", "😎"]
    
    async with httpx.AsyncClient() as client:
        tasks = [
            send_reaction_async(client, bot["token"], group_id, message_id, random.choice(premium_reactions)) 
            for bot in HELPER_BOTS
        ]
        await asyncio.gather(*tasks)
        