# bot.py
import logging
import random
import contextlib
import httpx
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

#      
from config import BOT_TOKEN, ADMIN_ID, VIP_PASSWORD, HELPER_BOTS
from database import init_db, generate_user_credentials, login_and_lock_group, is_group_allowed

#  
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

# ---     (FastAPI + Telegram Engine Connection) ---
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    #   
    init_db()
    
    #    
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("login", login))
    bot_app.add_handler(CommandHandler("setup", setup_group))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("gen", gen_key))
    bot_app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, auto_react))
    
    #    
    await bot_app.initialize()
    await bot_app.start()
    
    #    
    your_render_url = "https://onrender.com"
    await bot_app.bot.set_webhook(url=f"{your_render_url}/telegram")
    logging.info(f" Webhook successfully active at: {your_render_url}/telegram")
    
    yield
    #        
    await bot_app.stop()
    await bot_app.shutdown()

# FastAPI   (Lifespan  )
api_app = FastAPI(lifespan=lifespan)
bot_app = Application.builder().token(BOT_TOKEN).build()

@api_app.get("/")
def read_root():
    return {"status": "VIP 23-Bots Engine v21.3 is Online 24/7"}

@api_app.post("/telegram")
async def telegram_webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}

# ====================      ====================

async def start(update: Update, context):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            " !  23 --   \n\n"
            "         Access ID     :\n"
            "`/login [Access_ID] [Password]`"
        )

async def login(update: Update, context):
    if update.effective_chat.type != "private":
        return
    try:
        access_id = context.args[0]
        password = context.args[1]
        
        context.user_data['temp_access_id'] = access_id
        context.user_data['temp_password'] = password
        
        keyboard = []
        row = []
        for i, bot in enumerate(HELPER_BOTS, start=1):
            link = f"https://t.me{bot['username']}?startgroup=true"
            row.append(InlineKeyboardButton(text=f"  {i}", url=link))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            " *      !*\n\n"
            "          23      \n\n"
            " *:*       ,               :\n`/setup`",
            reply_markup=reply_markup, parse_mode="Markdown"
        )
    except IndexError:
        await update.message.reply_text("  : `/login [_Access_ID] [_]`")

async def setup_group(update: Update, context):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("        ")
        return
    
    if update.effective_user.id == ADMIN_ID:
        generate_user_credentials("ADMIN_TEST", "ADMIN_PASS", days=365)
        status = login_and_lock_group("ADMIN_TEST", "ADMIN_PASS", update.effective_chat.id)
        if status in ["success", "group_already_used"]:
            await update.message.reply_text("  :       !")
            return

    access_id = context.user_data.get('temp_access_id')
    password = context.user_data.get('temp_password')
    
    if not access_id or not password:
        await update.message.reply_text("         `/login` ,     ")
        return
        
    status = login_and_lock_group(access_id, password, update.effective_chat.id)
    
    if status == "success":
        await update.message.reply_text("  !             23  -   ")
    elif status == "group_already_used":
        await update.message.reply_text("          ")
    elif status == "wrong_group":
        await update.message.reply_text("            ")
    elif status == "expired":
        await update.message.reply_text("      (Expiry)    ")
    else:
        await update.message.reply_text("  !       ")

async def help_command(update: Update, context):
    help_text = (
        " *  :*\n\n"
        " `/start`      \n"
        " `/login [ID] [Password]`     \n"
        " `/setup`         "
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def gen_key(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        new_id = context.args[0]
        new_pass = context.args[1]
        days = int(context.args[2]) if len(context.args) > 2 else 30
        
        if generate_user_credentials(new_id, new_pass, days):
            await update.message.reply_text(f"   :\nID: `{new_id}`\nPass: `{new_pass}`\nDays: {days}")
        else:
            await update.message.reply_text("      ")
    except IndexError:
        await update.message.reply_text("  : `/gen [ID] [Password] [Days]`")

# ====================     ====================
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
    