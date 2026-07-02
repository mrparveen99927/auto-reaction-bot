# bot.py
import logging
import contextlib
import uvicorn
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN, HELPER_BOTS
from database import init_db
import user_handlers
import admin_handlers
import reaction_engine

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

# मेन एडमिन बोट
bot_app = Application.builder().token(BOT_TOKEN).build()

# फिक्स: 23 हेल्पर बोट्स के एप्लिकेशन्स को स्टोर करने के लिए लिस्ट
helper_apps = []

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    # 1. मेन बोट के हैंडलर्स रजिस्टर करना
    bot_app.add_handler(CommandHandler("start", user_handlers.start))
    bot_app.add_handler(CommandHandler("login", user_handlers.login))
    bot_app.add_handler(CommandHandler("setup", user_handlers.setup_group))
    bot_app.add_handler(CommandHandler("help", user_handlers.help_command))
    bot_app.add_handler(CommandHandler("status", user_handlers.status_command))
    
    bot_app.add_handler(CommandHandler("gen", admin_handlers.gen_key))
    bot_app.add_handler(CommandHandler("remkey", admin_handlers.rem_key))
    bot_app.add_handler(CommandHandler("stats", admin_handlers.stats_command))
    bot_app.add_handler(CommandHandler("users", admin_handlers.users_list))
    bot_app.add_handler(CommandHandler("broadcast", admin_handlers.broadcast))
    
    # ग्रुप और चैनल दोनों का फिल्टर
    bot_app.add_handler(MessageHandler((filters.ChatType.GROUPS | filters.ChatType.CHANNEL) & ~filters.COMMAND, reaction_engine.auto_react))
    
    await bot_app.initialize()
    await bot_app.start()
    
    # 2. फिक्स: सभी 23 हेल्पर बोट्स को बैकएंड में ज़िंदा (Start) करना
    for bot_info in HELPER_BOTS:
        try:
            h_app = Application.builder().token(bot_info["token"]).build()
            # हेल्पर बोट्स को भी मैसेज रीड करने के लिए सेम रिएक्शन इंजन देना
            h_app.add_handler(MessageHandler((filters.ChatType.GROUPS | filters.ChatType.CHANNEL) & ~filters.COMMAND, reaction_engine.auto_react))
            await h_app.initialize()
            await h_app.start()
            helper_apps.append(h_app)
            logging.info(f"Helper Bot Started Successfully: {bot_info['username']}")
        except Exception as e:
            logging.error(f"Failed to start helper {bot_info['username']}: {str(e)}")
    
    # रेंडर वेबहुक सेट करना
    your_render_url = "https://auto-reaction-bot-ayqv.onrender.com"
    await bot_app.bot.set_webhook(url=f"{your_render_url}/telegram")
    logging.info(f"Master Webhook active on: {your_render_url}/telegram")
    
    yield
    
    # बंद करते समय सबको स्टॉप करना
    for h_app in helper_apps:
        await h_app.stop()
        await h_app.shutdown()
        
    await bot_app.stop()
    await bot_app.shutdown()

api_app = FastAPI(lifespan=lifespan)

@api_app.get("/redirect/{bot_num}")
def redirect_to_bot(bot_num: int):
    bot_username = f"FastReact{bot_num}_bot"
    if bot_num == 20: bot_username = "FastReact21_bot"
    return RedirectResponse(url=f"https://telegram.me{bot_username}?startgroup=true")

@api_app.get("/")
def read_root(): return {"status": "VIP 23 Buttons Engine Online"}

@api_app.post("/telegram")
async def telegram_webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}

if __name__ == '__main__':
    uvicorn.run(api_app, host="0.0.0.0", port=10000)
    