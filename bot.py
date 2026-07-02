# bot.py
import logging
import random
import contextlib
import httpx
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Credentials and DB Imports
from config import BOT_TOKEN, ADMIN_ID, VIP_PASSWORD, HELPER_BOTS
from database import init_db, generate_user_credentials, login_and_lock_group, is_group_allowed

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

# FastAPI + Telegram Lifespan Engine
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("login", login))
    bot_app.add_handler(CommandHandler("setup", setup_group))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("gen", gen_key))
    bot_app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, auto_react))
    
    await bot_app.initialize()
    await bot_app.start()
    
    your_render_url = "https://onrender.com"
    await bot_app.bot.set_webhook(url=f"{your_render_url}/telegram")
    logging.info(f" Webhook active at: {your_render_url}/telegram")
    
    yield
    await bot_app.stop()
    await bot_app.shutdown()

api_app = FastAPI(lifespan=lifespan)
bot_app = Application.builder().token(BOT_TOKEN).build()

@api_app.get("/")
def read_root():
    return {"status": "VIP Clean Engine Button-Fix Online"}

@api_app.post("/telegram")
async def telegram_webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}

# ==================== BOT HANDLERS ====================

async def start(update: Update, context):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            " Welcome to VIP 23x Multi-Auto-Reaction Service!\n\n"
            " To login and get bot buttons, send your credentials like this:\n"
            "`/login [Access_ID] [Password]`"
        )

async def login(update: Update, context):
    if update.effective_chat.type != "private":
        return
    try:
        args = update.message.text.split()
        if len(args) < 3:
            await update.message.reply_text(" Use format: `/login [Access_ID] [Password]`")
            return
            
        access_id = args[1]
        password = args[2]
        
        context.user_data['temp_access_id'] = access_id
        context.user_data['temp_password'] = password
        
        keyboard = []
        row = []
        bot_count = 1
        
        for bot in HELPER_BOTS:
            username = bot.get("username", "").strip()
            #          
            if not username or username.lower() == "bot" or "?" in username:
                continue
                
            link = f"https://t.me{username}?startgroup=true"
            row.append(InlineKeyboardButton(text=f" Bot {bot_count}", url=link))
            bot_count += 1
            
            if len(row) == 2:
                keyboard.append(row)
                row = []
                
        if row:
            keyboard.append(row)
            
        if not keyboard:
            await update.message.reply_text(" Error: No valid helper bots found in config list.")
            return
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f" *Login Credentials Cached!*\n\n"
            f" ID: `{access_id}`\n"
            f" Now click the buttons below to ADD active bots to your group.\n\n"
            f" *Important:* After adding bots as Admin, go to your group and type:\n`/setup`",
            reply_markup=reply_markup, parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f" Error during login: {str(e)}")

async def setup_group(update: Update, context):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(" This command works only inside Telegram Groups.")
        return
    
    if update.effective_user.id == ADMIN_ID:
        generate_user_credentials("ADMIN_TEST", "ADMIN_PASS", days=365)
        status = login_and_lock_group("ADMIN_TEST", "ADMIN_PASS", update.effective_chat.id)
        if status in ["success", "group_already_used"]:
            await update.message.reply_text(" Owner Special: Group activated successfully!")
            return

    access_id = context.user_data.get('temp_access_id')
    password = context.user_data.get('temp_password')
    
    if not access_id or not password:
        await update.message.reply_text(" Please go to Bot PM and `/login` first, then run this command here.")
        return
        
    status = login_and_lock_group(access_id, password, update.effective_chat.id)
    
    if status == "success":
        await update.message.reply_text(" Congratulations! Your group is now LOCKED & VERIFIED. Reaction Blast is active!")
    elif status == "group_already_used":
        await update.message.reply_text(" This group is already locked with another license.")
    elif status == "wrong_group":
        await update.message.reply_text(" Your Access ID is already locked with a different group.")
    elif status == "expired":
        await update.message.reply_text(" Your VIP license has expired.")
    else:
        await update.message.reply_text(" Invalid Login Credentials! Please log in again in PM.")

async def help_command(update: Update, context):
    help_text = (
        " *Available Commands:*\n\n"
        " `/start`  Start the bot\n"
        " `/login [ID] [Password]`  Login and get buttons\n"
        " `/setup`  Run inside group to lock and start reactions."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def gen_key(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        args = update.message.text.split()
        if len(args) < 3:
            await update.message.reply_text(" Use format: `/gen [ID] [Password] [Days]`")
            return
            
        new_id = args[1]
        new_pass = args[2]
        days = int(args[3]) if len(args) > 3 else 30
        
        if generate_user_credentials(new_id, new_pass, days):
            await update.message.reply_text(f" VIP Credentials Generated:\nID: `{new_id}`\nPass: `{new_pass}`\nDays: {days}")
        else:
            await update.message.reply_text(" Error generating credentials.")
    except Exception as e:
        await update.message.reply_text(f" Format Error: {str(e)}")

# ==================== CORE AUTO REACTION ENGINE ====================
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
    premium_reactions = ["", "", "", "", "", "", "", "", "", ""]
    
    async with httpx.AsyncClient() as client:
        tasks = [
            send_reaction_async(client, bot["token"], group_id, message_id, random.choice(premium_reactions)) 
            for bot in HELPER_BOTS
        ]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    uvicorn.run(api_app, host="0.0.0.0", port=10000)
    