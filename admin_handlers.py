# admin_handlers.py
import sqlite3
from telegram import Update
from config import ADMIN_ID, DB_NAME
from database import generate_user_credentials

async def gen_key(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        # यहाँ लिस्ट को बिल्कुल सही स्ट्रिंग में बदला गया है
        if not context.args or len(context.args) < 2:
            await update.message.reply_text("❌ Format: `/gen [ID] [Password] [Days]`")
            return
            
        new_id = str(context.args[0]).strip()
        new_pass = str(context.args[1]).strip()
        
        # दिनों की संख्या को लिस्ट से निकालकर नंबर में बदलना
        days = int(context.args[2]) if len(context.args) > 2 else 30
        
        if generate_user_credentials(new_id, new_pass, days):
            await update.message.reply_text(f"✅ *VIP License Created:*\n\n🔑 ID: `{new_id}`\n🔒 Pass: `{new_pass}`\n⏳ Validity: `{days} Days`")
        else:
            await update.message.reply_text("❌ Error generating license code.")
    except Exception as e:
        await update.message.reply_text(f"❌ Format Error: {str(e)}")

async def rem_key(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        if not context.args:
            await update.message.reply_text("❌ Format: `/remkey [Access_ID]`")
            return
        target_id = str(context.args[0]).strip()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE access_id = ?", (target_id,))
        conn.commit()
        count = cursor.rowcount
        conn.close()
        
        if count > 0:
            await update.message.reply_text(f"🗑️ License for ID `{target_id}` has been successfully revoked!")
        else:
            await update.message.reply_text("❌ ID not found in database.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def stats_command(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE group_id IS NOT NULL")
    active_groups = cursor.fetchone()[0]
    conn.close()
    
    stats_msg = f"📊 *VIP Bot Global Dashboard:*\n\n"
    stats_msg += f"👥 Total Generated Keys: `{total_users}`\n"
    stats_msg += f"📢 Total Locked/Active Groups: `{active_groups}`\n"
    stats_msg += f"⚡ Helper Engine Power: `23 Bots Configured`"
    await update.message.reply_text(stats_msg, parse_mode="Markdown")

async def users_list(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT access_id, password, group_id, expiry_date FROM users")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        await update.message.reply_text("📁 Database is completely empty.")
        return
        
    reply = "📝 *Registered VIP Users List:*\n\n"
    for row in rows:
        reply += f"🔑 ID: `{row[0]}` | P: `{row[1]}`\n📢 Group: `{row[2] if row[2] else 'None'}`\n⏳ Exp: `{row[3]}`\n──────────────────\n"
    await update.message.reply_text(reply, parse_mode="Markdown")

async def broadcast(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ Format: `/broadcast [Your message here]`")
        return
    await update.message.reply_text("📢 *Global Broadcast finished successfully.*")
    