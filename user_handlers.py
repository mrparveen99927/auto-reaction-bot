# user_handlers.py के अंदर केवल login फ़ंक्शन को इससे रिप्लेस करें:
async def login(update: Update, context):
    if update.effective_chat.type != "private": return
    try:
        text_parts = update.message.text.split()
        if len(text_parts) < 3:
            await update.message.reply_text("❌ Format: `/login [ID] [Pass]` or `/login [ID] [Pass] [@username]`")
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
        
        # यूजरनेम और आईडी दोनों को ऑटोमैटिक हैंडल करने का फिक्स
        lock_msg = "Not locked yet. Run `/setup` inside group to activate."
        if len(text_parts) > 3:
            raw_chat_id = text_parts[3].strip()
            try:
                # 1. अगर ग्राहक ने @username डाला है
                if raw_chat_id.startswith('@'):
                    try:
                        chat_obj = await context.bot.get_chat(raw_chat_id)
                        target_chat_id = chat_obj.id  # टेलीग्राम खुद इसे -100xxx में बदल देगा
                    except Exception:
                        await update.message.reply_text("❌ बोट आपके चैनल को ढूंढ नहीं पाया! सुनिश्चित करें कि मेन बोट उस चैनल में एडमिन है।")
                        return
                # 2. अगर ग्राहक ने सीधा नंबर आईडी डाली है
                else:
                    target_chat_id = int(raw_chat_id)
                
                # डेटाबेस में सेव करें
                lock_status = await asyncio.to_thread(login_and_lock_group, access_id, "BYPASS_CHECK", target_chat_id)
                if lock_status == "success":
                    lock_msg = f"Locked to Chat ID: `{target_chat_id}`"
                elif lock_status == "group_already_used":
                    lock_msg = "⚠️ This group/channel is already locked with another license!"
                else:
                    lock_msg = "⚠️ License already bound to another chat."
            except ValueError:
                lock_msg = "⚠️ Invalid format! Use numbers or @username."

        msg = (
            f"✅ *Login Successful!*\n\n"
            f"🔑 VIP ID: `{access_id}`\n"
            f"📅 Expires On: `{expiry_date}`\n"
            f"📡 Status: *{lock_msg}*\n\n"
            f"🤖 *VIP Helper Bots List:* Configured successfully.\n"
            f"Make sure all 23 helper bots are **Admin** in your chat!"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Login Error: {str(e)}")
        