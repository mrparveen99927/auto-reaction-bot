# user_handlers.py
import sqlite3
import asyncio
from datetime import datetime
# फिक्स 1: यहाँ 'Update' क्लास को इम्पोर्ट कर दिया गया है जिससे NameError नहीं आएगी
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
            "1. Send: `/login [Access_ID] [Password] [Channel_ID_or_@Username]`\n"
            "_(Example: `/login key1 pass1 -10022334455` or `/login key1 pass1 @mychannel`)_\n\n"
            "Components: `/status` to check remaining license days.",
            parse_mode="Markdown"
        )

async def login(update: Update, context):
    if update.effective_chat.type != "private": return
    try:
        text_parts = update.message.text.split()
        if len(text_parts) < 3:
            await update.message.reply_text("❌ Format: `/login [ID] [Pass]` or `/login [ID] [Pass] [Channel_ID_or_@Username]`")
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
        
        # यूजरनेम और आईडी दोनों को ऑटोमैटिक हैंडल करने का लॉजिक
        lock_msg = "Not locked yet. Run `/setup` inside group to activate."
        if len(text_parts) > 3:
            raw_chat_id = text_parts[3].strip()
            try:
                if raw_chat_id.startswith('@'):
                    try:
                        chat_obj = await context.bot.get_chat(raw_chat_id)
                        target_chat_id = chat_obj.id
                    except Exception:
                        await update.message.reply_text("❌ बोट आपके चैनल को ढूंढ नहीं पाया! सुनिश्चित करें कि मेन बोट उस चैनल में एड敏 (Admin) है।")
                        return
                else:
                    target_chat_id = int(raw_chat_id)
                
                lock_status = await asyncio.to_thread(login_and_lock_group, access_id, "BYPASS_CHECK", target_chat_id)
                if lock_status == "success":
                    lock_msg = f"Locked to Chat ID: `{target_chat_id}`"
                elif lock_status == "group_already_used":
                    lock_msg = "⚠️ This group/channel is already locked with another license!"
                else:
                    lock_msg = "⚠️ License already bound to another chat."
            except ValueError:
                lock_msg = "⚠️ Invalid format! Use numbers or @username."

        # फिक्स 2: गायब हुई 23 बोट्स की पूरी लिस्ट को यहाँ वापस जोड़ दिया गया है (Touch to Copy फॉर्मेट में)
        msg = (
            f"✅ *Login Successful!*\n\n"
            f"🔑 VIP ID: `{access_id}`\n"
            f"📅 Expires On: `{expiry_date}`\n"
            f"📡 Status: *{lock_msg}*\n\n"
            f"🤖 *VIP Helper Bots List (Touch to Copy & Add as Admin):*\n\n"
        )
        for i in range(1, 24):
            bot_username = f"FastReact{i}_bot" if i != 20 else "FastReact21_bot"
            msg += f"{i}. `@{bot_username}`\n"
            
        msg += f"\n📢 *Important:* Make sure all 23 helper bots above are added as **Admin** in your channel/group with full reaction rights!"
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
    