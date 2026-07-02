# reaction_engine.py
import random
import asyncio
from telegram import Update
from telegram.ext import ExtBot
from config import HELPER_BOTS
from database import is_group_allowed

async def send_reaction_async(token, chat_id, message_id, reaction):
    try:
        # प्रत्येक हेल्पर बोट के टोकन से एक्सटर्नल बोट क्लाइंट बनाना
        async with ExtBot(token=token) as bot_client:
            await bot_client.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=[{"type": "emoji", "emoji": reaction}],
                is_big=True
            )
    except Exception:
        pass  # अगर कोई बोट एडमिन नहीं है या टोकन एक्सपायर्ड है तो एरर इग्नोर करें

async def auto_react(update: Update, context):
    # फिक्स 1: ग्रुप मैसेज और चैनल पोस्ट दोनों को एक साथ सपोर्ट करना
    target_msg = update.message or update.channel_post
    if not target_msg:
        return
        
    group_id = update.effective_chat.id
    if not is_group_allowed(group_id):
        return
        
    message_id = target_msg.message_id
    premium_reactions = ["👍", "❤", "🔥", "🎉", "🤩", "🚀", "🥰", "👏", "⚡", "😎"]
    
    # 23 हेल्पर बोट्स से एक साथ रिएक्शन भेजने का टास्क शेड्यूल करना
    tasks = [
        send_reaction_async(
            bot["token"], 
            group_id, 
            message_id, 
            random.choice(premium_reactions)
        )
        for bot in HELPER_BOTS
    ]
    await asyncio.gather(*tasks)
    