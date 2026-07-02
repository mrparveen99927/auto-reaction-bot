# user_handlers.py
from datetime import datetime
from telegram import Update
from config import ADMIN_ID
import database

async def start(update: Update, context):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "🚀 *VIP Multi-Auto-Reaction Bot Online!*\n\n"
            "📝 *For Groups Setup:*\n"
            "Send: `/login [Access_ID] [Password]` then run `/setup` in group.\n\n"
            "📢 *For Channels Setup:*\n"
            "Send: `/login [Access_ID] [Password] [Channel_ID_or_@Username]`\n\n"
            "⏳ Use `/status` to check remaining days.",
            parse_mode="Markdown"
        )

async def login(update: Update, context):
    if update.effective_chat.type != "private": return
    try:
        text_parts = update.message.text.split()
        if len(text_parts) < 3:
            await update.message.reply_text("❌ Format: `/login [ID] [Pass]` or `/login [ID] [Pass] [ChannelID_or_@Username]`")
            return
            
        access_id = str(text_parts[1]).strip()
        password = str(text_parts[2]).strip()
        
        res = await database.users_collection.find_one({"access_id": access_id})
        if not res or res.get("password") != password:
            await update.message.reply_text("❌ Invalid ID or Password!")
            return
            
        expiry_date = res.get("expiry_date")
        if res.get("status") != 'active' or datetime.now() > datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S'):
            await update.message.reply_text("❌ Your VIP license has expired!")
            return
            
        await database.save_chat_id(access_id, update.effective_chat.id)
        
        lock_msg = "Not locked yet. Run `/setup` inside group to activate."
        if len(text_parts) > 3:
            raw_chat_id = text_parts[3].strip()
            try:
                if raw_chat_id.startswith('@'):
                    try:
                        chat_obj = await context.bot.get_chat(raw_chat_id)
                        target_chat_id = chat_obj.id
                    except Exception:
                        await update.message.reply_text("❌ Channel not found! Admin the main bot first.")
                        return
                else:
                    target_chat_id = int(raw_chat_id)
                
                lock_status = await database.login_and_lock_group(access_id, "BYPASS_CHECK", target_chat_id)
                if lock_status == "success":
                    lock_msg = f"Locked to Chat ID: `{target_chat_id}`"
                elif lock_status == "group_already_used":
                    lock_msg = "⚠️ Chat already locked with another license!"
                else:
                    lock_msg = "⚠️ License bound to another chat."
            except ValueError:
                lock_msg = "⚠️ Invalid chat format."

        msg = (
            f"✅ *Login Successful!*\n\n"
            f"🔑 VIP ID: `{access_id}`\n"
            f"📅 Expires On: `{expiry_date}`\n"
            f"📡 Status: *{lock_msg}*\n\n"
            f"🤖 *VIP Helper Bots List (Touch to Copy):*\n\n"
        )
        for i in range(1, 24):
            bot_username = f"FastReact{i}_bot" if i != 20 else "FastReact21_bot"
            msg += f"{i}. `@{bot_username}`\n"
            
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Login Error: {str(e)}")

async def setup_group(update: Update, context):
    if update.effective_chat.type not in ["group", "supergroup"]: return
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        await database.generate_user_credentials("ADMIN_TEST", "ADMIN_PASS", days=365)
        status = await database.login_and_lock_group("ADMIN_TEST", "ADMIN_PASS", update.effective_chat.id)
        if status in ["success", "group_already_used"]:
            await update.message.reply_text("👑 Group activated for 365 Days!")
            return

    user_data = await database.users_collection.find_one({"chat_id": user_id})
    if not user_data:
        await update.message.reply_text("❌ Please go to Bot PM and `/login` first.")
        return
        
    access_id = user_data.get("access_id")
    status = await database.login_and_lock_group(access_id, "BYPASS_CHECK", update.effective_chat.id)
    if status == "success":
        await update.message.reply_text("🎉 Group Verified & Locked!")
    else:
        await update.message.reply_text("❌ Activation Error!")

async def status_command(update: Update, context):
    if update.effective_chat.type != "private": return
    user_id = update.effective_user.id
    user_data = await database.users_collection.find_one({"chat_id": user_id})
    if res := user_data:
        access_id = res.get("access_id")
        expiry_date = res.get("expiry_date")
        group_id = res.get("group_id", "Not Bound Yet")
        time_left = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S') - datetime.now()
        await update.message.reply_text(f"🔑 ID: `{access_id}`\n📡 Bound Chat: `{group_id}`\n⏳ Left: *{time_left.days} Days*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Not logged in.")

async def help_command(update: Update, context):
    await update.message.reply_text("Commands: `/start`, `/login`, `/status`, `/setup`")
    