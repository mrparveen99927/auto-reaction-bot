# admin_handlers.py
import sqlite3
import asyncio
from telegram import Update
from config import ADMIN_ID, DB_NAME
from database import generate_user_credentials

async def gen_key(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        text_parts = update.message.text.split()
        if len(text_parts) < 3:
            await update.message.reply_text(" Format: `/gen [ID] [Password] [Days]`")
            return
            
        new_id = str(text_parts[1]).strip()
        new_pass = str(text_parts[2]).strip()
        days = int(text_parts[3]) if len(text_parts) > 3 else 30
        
        if generate_user_credentials(new_id, new_pass, days):
            await update.message.reply_text(f" *VIP License Created:*\n\n ID: `{new_id}`\n Pass: `{new_pass}`\n Validity: `{days} Days`")
        else:
            await update.message.reply_text(" Error generating license code.")
    except Exception as e:
        await update.message.reply_text(f" Format Error: {str(e)}")

async def rem_key(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        text_parts = update.message.text.split()
        if len(text_parts) < 2:
            await update.message.reply_text(" Format: `/remkey [Access_ID]`")
            return
        target_id = str(text_parts[1]).strip()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE access_id = ?", (target_id,))
        conn.commit()
        count = cursor.rowcount
        conn.close()
        
        if count > 0:
            await update.message.reply_text(f" License for ID `{target_id}` has been successfully revoked!")
        else:
            await update.message.reply_text(" ID not found in database.")
    except Exception as e:
        await update.message.reply_text(f" Error: {str(e)}")

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
    
    stats_msg = f" *VIP Bot Global Dashboard:*\n\n"
    stats_msg += f" Total Generated Keys: `{total_users}`\n"
    stats_msg += f" Total Locked/Active Groups: `{active_groups}`\n"
    stats_msg += f" Helper Engine Power: `23 Bots Configured`"
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
        await update.message.reply_text(" Database is completely empty.")
        return
        
    reply = " *Registered VIP Users List:*\n\n"
    for row in rows:
        reply += f" ID: `{row[0]}` | P: `{row[1]}`\n Group: `{row[2] if row[2] else 'None'}`\n Exp: `{row[3]}`\n컴컴컴컴컴컴컴컴컴\n"
    await update.message.reply_text(reply, parse_mode="Markdown")

async def broadcast(update: Update, context):
    """   -          """
    if update.effective_user.id != ADMIN_ID:
        return
        
    #        
    text_parts = update.message.text.split(None, 1)
    if len(text_parts) < 2:
        await update.message.reply_text(" Format: `/broadcast [Your message here]`")
        return
        
    broadcast_msg = text_parts[1]
    await update.message.reply_text(" *Global Broadcast Initiated... Sending to all users...*")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users WHERE chat_id IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    
    success_count = 0
    fail_count = 0
    
    for row in rows:
        user_chat_id = row[0]
        try:
            #        
            await context.bot.send_message(chat_id=user_chat_id, text=f" *ADMIN NOTICE:*\n\n{broadcast_msg}", parse_mode="Markdown")
            success_count += 1
            await asyncio.sleep(0.2) #         
        except Exception:
            fail_count += 1
            
    await update.message.reply_text(f" *Broadcast Finished!*\n\n Successfully Sent: `{success_count}`\n Failed/Blocked: `{fail_count}`")
    