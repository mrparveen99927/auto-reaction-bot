# user_handlers.py
import sqlite3
import asyncio
from datetime import datetime
from telegram import Update
from config import ADMIN_ID, DB_NAME
from database import generate_user_credentials, login_and_lock_group, save_chat_id

def db_verify_user(access_id, password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT expiry_date, status FROM users WHERE access_id = ? AND password = ?", (access_id, password))
        return cursor.fetchone()

def db_get_status_by_tg_id(tg_user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT access_id, expiry_date, group_id FROM users WHERE chat_id = ?", (tg_user_id,))
        return cursor.fetchone()

async def start(update: Update, context):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            " *Welcome to VIP 23x Multi-Auto-Reaction Premium Service!*\n\n"
            " Use `/login [ID] [Password]` to check your helper bots list.\n"
            " Use `/status` anytime to check your license validity.\n"
            " Use `/help` to see all available features.",
            parse_mode="Markdown"
        )

async def login(update: Update, context):
    if update.effective_chat.type != "private":
        return
    try:
        text_parts = update.message.text.split()
        if len(text_parts) < 3:
            await update.message.reply_text(" Use format: `/login [Access_ID] [Password]`")
            return
        access_id = str(text_parts[1]).strip()
        password = str(text_parts[2]).strip()
        res = await asyncio.to_thread(db_verify_user, access_id, password)
        if not res:
            await update.message.reply_text(" Invalid ID or Password!")
            return
        expiry_date, status = res
        if status != 'active' or datetime.now() > datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S'):
            await update.message.reply_text(" Your VIP license has expired!")
            return
        await asyncio.to_thread(save_chat_id, access_id, update.effective_chat.id)
        msg = f" *Login Successful!*\n\n VIP ID: `{access_id}`\n Expires On: `{expiry_date}`\n\n"
        for i in range(1, 24):
            bot_username = f"FastReact{i}_bot" if i != 20 else "FastReact21_bot"
            msg += f"{i} `{bot_username}`\n"
        msg += f"\n *How to Add:*\n1. Add bots to group.\n2. Make them Admin.\n\n Run `/setup` inside group."
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f" Login Error: {str(e)}")

async def setup_group(update: Update, context):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(" This command works only inside Groups.")
        return
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        await asyncio.to_thread(generate_user_credentials, "ADMIN_TEST", "ADMIN_PASS", days=365)
        status = await asyncio.to_thread(login_and_lock_group, "ADMIN_TEST", "ADMIN_PASS", update.effective_chat.id)
        if status in ["success", "group_already_used"]:
            await update.message.reply_text(" *Owner Special:* Activated for 365 Days!")
            return
    user_data = await asyncio.to_thread(db_get_status_by_tg_id, user_id)
    if not user_data:
        await update.message.reply_text(" Please go to Bot PM and `/login` first.")
        return
    access_id, _, _ = user_data
    status = await asyncio.to_thread(login_and_lock_group, access_id, "BYPASS_CHECK", update.effective_chat.id)
    if status == "success":
        await update.message.reply_text(" *Congratulations!* Group LOCKED & VERIFIED.")
    elif status == "group_already_used":
        await update.message.reply_text(" This group is already locked.")
    else:
        await update.message.reply_text(" Activation Error!")

async def status_command(update: Update, context):
    if update.effective_chat.type != "private":
        return
    user_id = update.effective_user.id
    user_data = await asyncio.to_thread(db_get_status_by_tg_id, user_id)
    if res := user_data:
        access_id, expiry_date, group_id = res
        time_left = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S') - datetime.now()
        await update.message.reply_text(f" ID: `{access_id}`\nGroup: `{group_id}`\nRemaining: {time_left.days} Days", parse_mode="Markdown")
    else:
        await update.message.reply_text(" Not logged in.")

async def help_command(update: Update, context):
    await update.message.reply_text("`/start`, `/login`, `/status`, `/setup`", parse_mode="Markdown")
    