# bot.py
import logging
import contextlib
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Sub-modules imports
from config import BOT_TOKEN
from database import init_db
import user_handlers
import admin_handlers
import reaction_engine

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables at startup
    init_db()
    
    # Register Core Bot Handlers from user_handlers.py
    bot_app.add_handler(CommandHandler("start", user_handlers.start))
    bot_app.add_handler(CommandHandler("login", user_handlers.login))
    bot_app.add_handler(CommandHandler("setup", user_handlers.setup_group))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("status", user_handlers.status_command))
    
    # Admin Panel Handlers from admin_handlers.py
    bot_app.add_handler(CommandHandler("gen", admin_handlers.gen_key))
    bot_app.add_handler(CommandHandler("remkey", admin_handlers.rem_key))
    bot_app.add_handler(CommandHandler("stats", admin_handlers.stats_command))
    bot_app.add_handler(CommandHandler("users", admin_handlers.users_list))
    bot_app.add_handler(CommandHandler("broadcast", admin_handlers.broadcast))
    
    # Message interceptor for multi-reaction blast
    bot_app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, reaction_engine.auto_react))
    
    await bot_app.initialize()
    await bot_app.start()
    
    your_render_url = "https://auto-reaction-bot-ayqv.onrender.com"
    await bot_app.bot.set_webhook(url=f"{your_render_url}/telegram")
    logging.info(f" Masters Modular Webhook set to: {your_render_url}/telegram")
    
    yield
    await bot_app.stop()
    await bot_app.shutdown()

api_app = FastAPI(lifespan=lifespan)
bot_app = Application.builder().token(BOT_TOKEN).build()

# Smart URL redirect bypass logic (Updated to force-open inside Telegram App directly)
@api_app.get("/redirect/{bot_num}")
def redirect_to_bot(bot_num: int):
    bot_username = f"FastReact{bot_num}_bot"
    if bot_num == 20:
        bot_username = "FastReact21_bot"
    
    #  tg:// official deep link             
    return RedirectResponse(url=f"tg://resolve?domain={bot_username}&startgroup=true")

@api_app.get("/")
def read_root():
    return {"status": "VIP 23-Buttons Deep-Link Engine Online"}

@api_app.post("/telegram")
async def telegram_webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}

if __name__ == '__main__':
    uvicorn.run(api_app, host="0.0.0.0", port=10000)
    