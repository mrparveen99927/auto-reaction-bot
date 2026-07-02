# user_handlers.py
import sqlite3
from datetime import datetime
from telegram import Update
from config import ADMIN_ID, DB_NAME
from database import generate_user_credentials, login_and_lock_group, is_group_allowed

async def start(update: Update, context):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "👋 *Welcome to VIP 23x Multi-Auto-Reaction Premium Service!*\n\n"
            "🔹 Use `/login [ID] [Password]` to check your helper bots list.\n"
            "🔹 Use `/status` anytime to check your license validity.\n"
            "🔹 Use `/help` to see all available features.",
            parse_mode="Markdown"
        )

async def login(update: Update, context):
    if update.effective_chat.type != "private":
        return
    try:
        if not context.args or len(context.args) < 2:
            await update.message.reply_text("❌ Use format: `/login [Access_ID] [Password]`")
            return
            
        access_id = str(context.args).strip()
        password = str(context.args).strip()
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT expiry_date, status FROM users WHERE access_id = ? AND password = ?", (access_id, password))
        res = cursor.fetchone()
        conn.close()
        
        if not res:
            await update.message.reply_text("❌ Invalid ID or Password! Please contact owner.")
            return
            
        expiry_date, status = res
        if status != 'active' or datetime.now() > datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S'):
            await update.message.reply_text("❌ Your VIP license has expired or been disabled!")
            return
        
        context.user_data['temp_access_id'] = access_id
        context.user_data['temp_password'] = password
        
        # 100% वर्किंग 'टच-टू-कॉपी' टेक्स्ट लिस्ट लॉजिक
        msg = f"🎉 *Login Successful!*\n\n"
        msg += f"🔑 VIP ID: `{access_id}`\n"
        msg += f"⏳ Expires On: `{expiry_date}`\n\n"
        msg += "📋 *VIP Helper Bots List (Touch to Copy):*\n"
        msg += "👇 _नीचे दिए गए यूजरनेम पर बस एक बार क्लिक करें, वह कॉपी हो जाएगा:_\n\n"
        
        for i in range(1, 24):
            bot_username = f"FastReact{i}_bot"
            if i == 20:
                bot_username = "FastReact21_bot"  # गैप फिक्स
            
            # ` ` लगाने से यह टेक्स्ट मोनो-स्पेस बन जाता है, जिसपर क्लिक करते ही सीधे कॉपी हो जाता है
            msg += f"{i}️⃣ `{bot_username}`\n"
            
        msg += f"\n⚙️ *How to Add:*\n"
        msg += f"1️⃣ ऊपर की लिस्ट से एक-एक करके यूजरनेम पर क्लिक करके कॉपी करें।\n"
        msg += f"2️⃣ अपने ग्रुप में जाकर उन्हें मेंबर की तरह जोड़ें और **Admin** बना दें।\n\n"
        msg += f"⚠️ *Important:* सभी बॉट्स को शामिल करने के बाद ग्रुप में जाकर टाइप करें: `/setup`"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Login Error: {str(e)}")

async def setup_group(update: Update, context):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command works only inside Telegram Groups.")
        return
        
    if update.effective_user.id == ADMIN_ID:
        generate_user_credentials("ADMIN_TEST", "ADMIN_PASS", days=365)
        status = login_and_lock_group("ADMIN_TEST", "ADMIN_PASS", update.effective_chat.id)
        if status in ["success", "group_already_used"]:
            await update.message.reply_text("🎉 *Owner Special:* Group activated and locked successfully for 365 Days!")
            return

    access_id = context.user_data.get('temp_access_id')
    password = context.user_data.get('temp_password')
    
    if not access_id or not password:
        await update.message.reply_text("❌ Please go to Bot PM and `/login` first, then run `/setup` here.")
        return
        
    status = login_and_lock_group(access_id, password, update.effective_chat.id)
    
    if status == "success":
        await update.message.reply_text("🎉 *Congratulations!* Your group is now LOCKED & VERIFIED. 23x Blast is active!")
    elif status == "group_already_used":
        await update.message.reply_text("❌ This group is already locked with another license.")
    elif status == "wrong_group":
        await update.message.reply_text("❌ Your Access ID is already locked with a different group.")
    elif status == "expired":
        await update.message.reply_text("❌ Your VIP license has expired.")
    else:
        await update.message.reply_text("❌ Invalid Session! Please log in again in Bot PM.")

async def status_command(update: Update, context):
    if update.effective_chat.type != "private":
        return
    access_id = context.user_data.get('temp_access_id')
    if not access_id:
        await update.message.reply_text("❌ You are not logged in. Please use `/login` first.")
        return
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT expiry_date, group_id FROM users WHERE access_id = ?", (access_id,))
    res = cursor.fetchone()
    conn.close()
    
    if res:
        expiry_date, group_id = res
        time_left = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S') - datetime.now()
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        status_msg = f"ℹ️ *Your VIP License Status:*\n\n"
        status_msg += f"🔑 ID: `{access_id}`\n"
        status_msg += f"🔒 Locked Group ID: `{group_id if group_id else 'Not Locked Yet'}`\n"
        status_msg += f"⏳ Time Remaining: *{days} Days, {hours} Hours, {minutes} Minutes*"
        await update.message.reply_text(status_msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Session error or key deleted.")

async def help_command(update: Update, context):
    help_text = (
        "ℹ️ *Available Commands Guide:*\n\n"
        "🔹 `/start` ➡️ Activate Inbox Session\n"
        "🔹 `/login [ID] [Pass]` ➡️ Check Key & Get Bots List\n"
        "🔹 `/status` ➡️ Check your remaining days & time\n"
        "🔹 `/setup` ➡️ Run inside group to lock & deploy bots"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")
    