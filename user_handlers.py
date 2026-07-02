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
            "🚀 *VIP Multi-Auto-Reaction Bot Online!*\n\n"
            "📝 *For Groups Setup:*\n"
            "1. Send: `/login [Access_ID] [Password]`\n"
            "2. Go to your Group and send `/setup`\n\n"
            "📢 *For Channels Setup (Direct Bypass):*\n"
            "1. Send: `/login [Access_ID] [Password] [Channel_ID]`\n"
            "_(Example: `/login key1 pass1 -10022334455`)_\n\n"
            "⏱ Use `/status` to check remaining license days.",
            parse_mode="Markdown"
        )

async def login(update: Update, context):
    if update.effective_chat.type != "private": return
    try:
        text_parts = update.message.text.split()
        if len(text_parts) < 3:
            await update.message.reply_text("❌ Format: `/login [ID] [Pass]` or `/login [ID] [Pass] [Channel_ID]`")
            return
            
        access_id = str(text_parts[1]).strip()
        password = str(text_parts[2]).strip()
        
        res = await asyncio.to_thread(db_verify_user, access_id, password)
        if not res:
            await update.message.reply_text("❌ Invalid ID or Password!")
            return
            
        expiry_date, status = res
        if status != 'active' or datetime.now() > datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S'):
            await update.message.reply_text("❌ Your VIP license has expired!")
            return
            
        await asyncio.to_thread(save_chat_id, access_id, update.effective_chat.id)
        
        # चैनल आईडी डायरेक्ट बायपास फिक्स
        channel_locked = False
        if len(text_parts) > 3:
            try:
                target_chat_id = int(text_parts[3].strip())
                lock_status = await asyncio.to_thread(login_and_lock_group, access_id, "BYPASS_CHECK", target_chat_id)
                if lock_status == "success":
                    channel_locked = True
                    lock_msg = f"Locked to Channel/Group ID: `{target_chat_id}`"
                elif lock_status == "group_already_used":
                    lock_msg = "⚠️ This ID is already locked with another license!"
                else:
                    lock_msg = "⚠️ License already bound to another group/channel."
            except ValueError:
                lock_msg = "⚠️ Invalid Channel ID format! Must be numbers (e.g. -100xxx)."
        else:
            lock_msg = "Not locked yet. Run `/setup` inside group to activate."

        msg = (
            f"✅ *Login Successful!*\n\n"
            f"🔑 VIP ID: `{access_id}`\n"
            f"📅 Expires On: `{expiry_date}`\n"
            f"📡 Status: *{lock_msg}*\n\n"
            f"🤖 *VIP Helper Bots List:* Added successfully.\n"
            f"Make sure all 23 helper bots are **Admin** with full posting/reaction rights!"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Login Error: {str(e)}")

async def setup_group(update: Update, context):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command works only inside Telegram Groups.")
        return
        
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        await asyncio.to_thread(generate_user_credentials, "ADMIN_TEST", "ADMIN_PASS", days=365)
        status = await asyncio.to_thread(login_and_lock_group, "ADMIN_TEST", "ADMIN_PASS", update.effective_chat.id)
        if status in ["success", "group_already_used"]:
            await update.message.reply_text("👑 *Owner Special:* Group activated for 365 Days!")
            return

    user_data = await asyncio.to_thread(db_get_status_by_tg_id, user_id)
    if not user_data:
        await update.message.reply_text("❌ Please go to Bot PM and `/login` first.")
        return
        
    access_id, _, _ = user_data
    status = await asyncio.to_thread(login_and_lock_group, access_id, "BYPASS_CHECK", update.effective_chat.id)
    
    if status == "success":
        await update.message.reply_text("🎉 *Congratulations!* Your group is locked. 23x Blast Active!")
    elif status == "group_already_used":
        await update.message.reply_text("❌ This group is already locked with another license.")
    elif status == "wrong_group":
        await update.message.reply_text("❌ Your Access ID is already locked with a different chat.")
    else:
        await update.message.reply_text("❌ Activation Error!")

async def status_command(update: Update, context):
    if update.effective_chat.type != "private": return
    user_id = update.effective_user.id
    user_data = await asyncio.to_thread(db_get_status_by_tg_id, user_id)
    if res := user_data:
        access_id, expiry_date, group_id = res
        time_left = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S') - datetime.now()
        status_msg = (
            f"ℹ️ *Your VIP Status:*\n\n"
            f"🔑 ID: `{access_id}`\n"
            f"📡 Bound Chat ID: `{group_id if group_id else 'Not Bound Yet'}`\n"
            f"⏳ Time Left: *{time_left.days} Days*"
        )
        await update.message.reply_text(status_msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ You are not logged in. Use `/login` first.")

async def help_command(update: Update, context):
    await update.message.reply_text("Commands: `/start`, `/login`, `/status`, `/setup`", parse_mode="Markdown")
    