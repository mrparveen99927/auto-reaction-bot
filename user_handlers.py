# user_handlers.py - कस्टमर्स के कमांड्स और सख्त लॉगिन

from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
import database

BOT_LIST_TEXT = """
@FastReact1_bot   | @FastReact2_bot   | @FastReact3_bot
@FastReact4_bot   | @FastReact5_bot   | @FastReact6_bot
@FastReact7_bot   | @FastReact8_bot   | @FastReact9_bot
@FastReact10_bot  | @FastReact11_bot  | @FastReact12_bot
@FastReact13_bot  | @FastReact14_bot  | @FastReact15_bot
@FastReact16_bot  | @FastReact17_bot  | @FastReact18_bot
@FastReact19_bot  | @FastReact20_bot  | @FastReact21_bot
@FastReact22_bot  | @FastReact23_bot
"""

@Client.on_message(filters.command("start") & filters.private)
async def start_command(_, message: Message):
    await message.reply_text(
        "👋 **VIP 23x Reaction Bot में आपका स्वागत है!**\n\n"
        "अपना प्रीमियम एक्सेस चालू करने के लिए इस फॉर्मेट में लॉगिन करें:\n"
        "`/login [vip_id] [password] [@your_channel_username]`"
    )

@Client.on_message(filters.command("login") & filters.private)
async def login_command(client: Client, message: Message):
    args = message.command
    if len(args) < 4:
        await message.reply_text("❌ **लॉगिन फॉर्मेट गलत है!**\nयूज़ करें: `/login [vip_id] [password] [@channel]`")
        return
    
    vip_id, password, target_chat = args[1], args[2], args[3]
    
    # 1. डेटाबेस से आईडी-पासवर्ड मैच करना
    account = await database.get_vip_user(vip_id)
    if not account or account["password"] != password:
        await message.reply_text("❌ गलत VIP ID या पासवर्ड। कृपया सही क्रेडेंशियल्स डालें।")
        return
        
    if account["status"] == "Banned":
        await message.reply_text("🚫 आपका यह अकाउंट एडमिन द्वारा ब्लॉक (Banned) कर दिया गया है!")
        return

    if datetime.now() > account["expires_on"]:
        await message.reply_text("⏳ आपका प्रीमियम प्लान समाप्त (Expire) हो चुका है! कृपया रिन्यू कराएं।")
        return

    # 2. चैनल/ग्रुप की असली न्यूमेरिकल ID (-100...) निकालना
    try:
        chat_info = await client.get_chat(target_chat)
        chat_id = str(chat_info.id)
    except Exception:
        await message.reply_text("❌ बॉट आपके चैनल को ढूंढ नहीं पाया। सुनिश्चित करें कि चैनल पब्लिक है या हमारा मेन बॉट उसमें मेंबर है।")
        return

    # 3. सख्त वन-टाइम लॉक नियम (Strict Security Lock)
    if account["chat_id"] and account["chat_id"] != chat_id:
        await message.reply_text(f"❌ **सुरक्षा नियम:** यह VIP ID पहले से ही किसी दूसरे चैनल ID (`{account['chat_id']}`) पर लॉक है! आप इसे नए चैनल में इस्तेमाल नहीं कर सकते।")
        return

    # डेटाबेस में चैट आईडी लॉक करना
    await database.lock_user_to_chat(vip_id, chat_id, message.from_user.id)
    
    # ग्राहकों को दिखाने वाला डैशबोर्ड (जैसा आपके स्क्रीनशॉट में था)
    dashboard = (
        f"✅ **Login Successful!**\n\n"
        f"🔑 **VIP ID:** {vip_id}\n"
        f"📅 **Expires On:** {account['expires_on'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"🔒 **Status:** Locked to Chat ID: `{chat_id}`\n\n"
        f"🤖 **VIP Helper Bots List (Touch to Copy):**\n"
        f"{BOT_LIST_TEXT}\n\n"
        f"ℹ️ *इन सभी 23 बॉट्स को अपने चैनल में Admin बनाएं (मैसेज भेजने/रिएक्ट करने की अनुमति के साथ)। पोस्ट आते ही रिएक्शंस ऑटोमैटिक शुरू हो जाएंगे!*"
    )
    await message.reply_text(dashboard)
    