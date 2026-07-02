# reaction_engine.py - 23   -  

import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message
import config
import database

#      ' '       
# :      api_id  api_hash    
master_bot = Client(
    "MasterHelper", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH, 
    bot_token=config.HELPER_TOKENS[0]
)

@master_bot.on_message(filters.chat() & ~filters.service)
async def on_new_post_detected(_, message: Message):
    chat_id = str(message.chat.id)
    
    # 1.         
    is_active = await database.check_chat_permission(chat_id)
    
    #     ,   ,  30       ,     
    if not is_active:
        return

    print(f" [LOCK CHECK PASSED] New post in Chat ID: {chat_id}. Dispatching 23x reactions...")

    # 2. -  (0.2s)    23   -  
    for index, token in enumerate(config.HELPER_TOKENS):
        try:
            #           
            async with Client(f"worker_bot_{index}", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=token) as worker:
                #           
                chosen_reaction = random.choice(config.REACTIONS_POOL)
                
                await worker.send_reaction(
                    chat_id=message.chat.id, 
                    message_id=message.id, 
                    values=chosen_reaction
                )
                #     0.2        
                await asyncio.sleep(0.2)
                
        except Exception as e:
            print(f" Bot {index+1} encountered an error: {e}")
            continue

async def start_reaction_engine():
    """    bot.py         """
    print(" Reaction Engine is initialized and listening to VIP channels...")
    await master_bot.start()
    