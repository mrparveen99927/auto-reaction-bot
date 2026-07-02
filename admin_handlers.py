# admin_handlers.py
import sqlite3
import asyncio
from telegram import Update
from config import ADMIN_ID, DB_NAME
from database import generate_user_credentials

def db_delete_key(target_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE access_id = ?", (target_id,))
        conn.commit()
        return cursor.rowcount

def db_get_stats():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM users WHERE group_id IS NOT NULL")
        active_groups = cursor.fetchone()
        return total_users[0], active_groups[0]

def db_get_users():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT access_id, password, group_id, expiry_date FROM users")
        return cursor.fetchall()

def db_get_broadcast_chats():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users WHERE chat_id IS NOT NULL")
        return cursor.fetchall()

async def gen_key(update: Update, context):
    if update.effective_user.id != ADMIN_ID: return
    try:
        text_parts = update.message.text.split()
        if len(text_parts) < 3:
            await update.message.reply_text("Format: /gen [ID] [Password] [Days]")
            return
        new_id, new_pass = text_parts[1], text_parts[2]
        days = int(text_parts[3]) if len(text_parts) > 3 else 30
        if await asyncio.to_thread(generate_user_credentials, new_id, new_pass, days):
            await update.message.reply_text(f"VIP Key Created.\nID: `{new_id}`\nPass: `{new_pass}`", parse_mode="Markdown")
    except Exception as e: await update.message.reply_text(str(e))

async def rem_key(update: Update, context):
    if update.effective_user.id != ADMIN_ID: return
    try:
        text_parts = update.message.text.split()
        if len(text_parts) < 2: return
        target_id = text_parts[1]
        if await asyncio.to_thread(db_delete_key, target_id) > 0:
            await update.message.reply_text("Deleted successfully.")
    except Exception as e: await update.message.reply_text(str(e))

async def stats_command(update: Update, context):
    if update.effective_user.id != ADMIN_ID: return
    t, a = await asyncio.to_thread(db_get_stats)
    await update.message.reply_text(f"Total Keys: {t}\nActive Groups: {a}")

async def users_list(update: Update, context):
    if update.effective_user.id != ADMIN_ID: return
    rows = await asyncio.to_thread(db_get_users)
    reply = "VIP Users:\n"
    for r in rows: reply += f"ID: {r[0]} | Bound Chat: {r[2]}\n"
    await update.message.reply_text(reply)

async def broadcast(update: Update, context):
    if update.effective_user.id != ADMIN_ID: return
    text_parts = update.message.text.split(None, 1)
    if len(text_parts) < 2: return
    msg = text_parts[1]
    chats = await asyncio.to_thread(db_get_broadcast_chats)
    for c in chats:
        try:
            await context.bot.send_message(chat_id=c[0], text=f"NOTICE:\n\n{msg}")
            await asyncio.sleep(0.2)
        except: pass
    await update.message.reply_text("Broadcast Done.")
    