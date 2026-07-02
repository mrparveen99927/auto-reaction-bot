# reaction_engine.py
import random
import asyncio
from telegram import Update
from telegram.ext import ExtBot
from config import HELPER_BOTS
from database import is_group_allowed

async def send_reaction_async(token, chat_id, message_id, reaction):
    try:
        async with ExtBot(token=token) as bot_client:
            await bot_client.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=[{"type": "emoji", "emoji": reaction}],
                is_big=True
            )
    except: pass

async def auto_react(update: Update, context):
    target_msg = update.message or update.channel_post
    if not target_msg: return
    
    group_id = update.effective_chat.id
    if not await is_group_allowed(group_id): return
    
    premium_reactions = ["👍", "❤", "🔥", "🎉", "🤩", "🚀", "🥰", "👏", "⚡", "😎"]
    tasks = [
        send_reaction_async(bot["token"], group_id, target_msg.message_id, random.choice(premium_reactions))
        for bot in HELPER_BOTS
    ]
    await asyncio.gather(*tasks)
    