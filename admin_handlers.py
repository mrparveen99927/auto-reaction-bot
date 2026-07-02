# admin_handlers.py - सिर्फ आपके (Admin) कमांड्स

from pyrogram import Client, filters
from pyrogram.types import Message
import config
import database

@Client.on_message(filters.command("gen") & filters.user(config.ADMIN_ID))
async def gen_command(_, message: Message):
    args = message.command
    if len(args) < 4:
        await message.reply_text("❌ **गलत फॉर्मेट!**\nयूज़ करें: `/gen [id] [password] [days]`")
        return
    
    vip_id, password, days = args[1], args[2], int(args[3])
    expiry = await database.add_or_renew_user(vip_id, password, days)
    
    await message.reply_text(
        f"✅ **VIP Account Created Successfully!**\n\n"
        f"🔑 **ID:** `{vip_id}`\n"
        f"🔒 **Pass:** `{password}`\n"
        f"⏳ **Validity:** {days} Days\n"
        f"📅 **Expires On:** {expiry.strftime('%Y-%m-%d %H:%M:%S')}"
    )

@Client.on_message(filters.command("ban") & filters.user(config.ADMIN_ID))
async def ban_command(_, message: Message):
    args = message.command
    if len(args) < 2:
        await message.reply_text("❌ **गलत फॉर्मेट!**\nयूज़ करें: `/ban [vip_id]`")
        return
    
    vip_id = args[1]
    success = await database.ban_vip_user(vip_id)
    if success:
        await message.reply_text(f"🚫 VIP ID `{vip_id}` को सफलतापूर्वक **बैन** कर दिया गया है।")
    else:
        await message.reply_text("❌ यह VIP ID डेटाबेस में नहीं मिली।")

@Client.on_message(filters.command("stats") & filters.user(config.ADMIN_ID))
async def stats_command(_, message: Message):
    total, active, banned, locked = await database.get_db_stats()
    stats_msg = (
        f"📊 **Reaction Bot Live Stats:**\n\n"
        f"👥 कुल VIP आईडी: {total}\n"
        f"🟢 एक्टिव यूज़र्स: {active}\n"
        f"🚫 बैन यूज़र्स: {banned}\n"
        f"🔒 लॉक्ड चैनल/ग्रुप्स: {locked}"
    )
    await message.reply_text(stats_msg)
    