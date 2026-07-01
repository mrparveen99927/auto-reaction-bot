import logging
import random
import asyncio
import httpx
import uvicorn
from fastapi import FastAPI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# आपका मुख्य मास्टर बॉट टोकन
BOT_TOKEN = "8843244865:AAGS47kvrD-ZeOTr-EgxSYFoYY-Cg3SJk-A"
ADMIN_ID = 1780858471  

# आपका सीक्रेट वीआईपी पासवर्ड जो आप ग्राहकों को बेचेंगे (आप इसे कभी भी बदल सकते हैं)
VIP_PASSWORD = "PREMIUM_VIP_2026"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

# रेंडर को खुश रखने के लिए लाइटवेट वेब सर्वर
api_app = FastAPI()

@api_app.get("/")
def read_root():
    return {"status": "VIP 23-Bots Engine is Online 24/7"}

# सभी 23 बॉट्स की बिल्कुल सटीक लिस्ट
HELPER_BOTS = [
    {"token": "7759702480:AAF9Wts-mQJwo-kABbLH-07efM8oKicdhcM", "username": "FastReact1_bot"},
    {"token": "8868273049:AAGbuicV1ytedATSges9dzVeOoBrKbpVfkw", "username": "FastReact2_bot"},
    {"token": "8465196381:AAFkCeVgwlzdJKjm80S8bC248AQ3Q4lKzNw", "username": "FastReact3_bot"},
    {"token": "8990617369:AAGcVjb__c0DPfYyrPteEg3RqtvI75OVMJU", "username": "FastReact4_bot"},
    {"token": "8762982479:AAFpoIEsDKmgNG16Ql56J6F-OPY_1dGGQVg", "username": "FastReact5_bot"},
    {"token": "8616922120:AAEZ8xHmIIfqxGMQUkbEHOIGplIPT5uJsc4", "username": "FastReact6_bot"},
    {"token": "8954445996:AAEvH-lySAk5FGWX96Bv3i7FA3Dp1X9icVg", "username": "FastReact7_bot"},
    {"token": "8728914922:AAHmWtKYSr_y7Fy9oOYzxMQHgJYze3dmkVk", "username": "FastReact8_bot"},
    {"token": "8402811457:AAHfQIaYHFdBw12pF9zoapl29nYjRhBIUjs", "username": "FastReact9_bot"},
    {"token": "8504826070:AAHAVnCIh0kOMqqFW6UX7nfVOFuRuSmjZJY", "username": "FastReact10_bot"},
    {"token": "8864706900:AAG3kAzTOzUDiAlkI-Fahn3V5zyP8MTnhqY", "username": "FastReact11_bot"},
    {"token": "8712704500:AAG73EN_YxzXFR7k3pZVSzSLHse99abIz3o", "username": "FastReact12_bot"},
    {"token": "8472836823:AAEgwxV2fldYR7KNPlRVdRwjml03-Rpo9h4", "username": "FastReact13_bot"},
    {"token": "8519620118:AAESBKU5JF2LrqNvaufnO3u9aFCLZ8iuElQ", "username": "FastReact14_bot"},
    {"token": "8519620118:AAESBKU5JF2LrqNvaufnO3u9aFCLZ8iuElQ", "username": "FastReact15_bot"},
    {"token": "8684813874:AAFRp1IdRH9Cv19T7g_3BDynCPoy_DAGseA", "username": "FastReact15_bot"},
    {"token": "8724817204:AAGg2Z4VTcqpQPAJfqLJCUZyPWurQdeDi4g", "username": "FastReact15_bot"},
    {"token": "8818097026:AAFeL60mwgwhngaVxSSHtkdAru2F260Nprg", "username": "FastReact15_bot"},
    {"token": "8906790488:AAHiY5IqITVi6LC7mC6cvil79TOHqeU6L_Y", "username": "FastReact15_bot"},
    {"token": "8648415907:AAF0FtTCBtKr7ATqIJmKmdVgR9mLIXaUw5A", "username": "FastReact15_bot"},
    {"token": "8649993032:AAFzyrnLIMz9MP5lH9uJRb8t7xX98ngk9OA", "username": "FastReact21_bot"},
    {"token": "8996480629:AAHMUotLfpF7312HZLP4xuPiUx1EGQ1bXHc", "username": "FastReact22_bot"},
    {"token": "8963701519:AAHJ5GfL6yavqWuTr9ixGxdMc6V1JSiqSbI", "username": "FastReact23_bot"}
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "👋 नमस्ते! वीआईपी 23× मल्टी-ऑटो-रिएक्शन सर्विस में आपका स्वागत है।\n\n"
            "👉 लॉगिन करने के लिए अपना सीक्रेट पासवर्ड इस तरह भेजें:\n"
            "`/login आपका_पासवर्ड`"
        )
        async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    try:
        user_password = context.args[0]
        
        # पासवर्ड चेक करना (डेटाबेस का झंझट ही खत्म)
        if user_password == VIP_PASSWORD or update.effective_user.id == ADMIN_ID:
            context.user_data['is_vip'] = True
            
            keyboard = []
            row = []
            for i, bot in enumerate(HELPER_BOTS, start=1):
                link = f"https://t.me{bot['username']}?startgroup=true"
                row.append(InlineKeyboardButton(text=f"➕ बॉट {i}", url=link))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🎉 *लॉगिन सफल! आप वीआईपी मेंबर हैं।*\n\n"
                "🔥 अब नीचे दिए गए बटनों पर क्लिक करके सभी 23 बॉट्स को अपने ग्रुप में जोड़ें।\n\n"
                "⚠️ *महत्वपूर्ण:* सभी बॉट्स को शामिल करने के बाद, अपने ग्रुप में जाकर यह कमांड भेजें:\n`/setup`",
                reply_markup=reply_markup, parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ गलत पासवर्ड! कृपया सही वीआईपी एक्सेस कोड दर्ज करें।")
    except IndexError:
        await update.message.reply_text("❌ सही तरीका: `/login आपका_पासवर्ड`")

async def setup_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ यह कमांड केवल ग्रुप के अंदर काम करेगी।")
        return
        
    if context.user_data.get('is_vip') or update.effective_user.id == ADMIN_ID:
        # ग्रुप आईडी को थोड़ी देर के लिए चैट सेटिंग्स में सेव कर देते हैं ताकि बॉट एक्टिव रहे
        context.chat_data['active'] = True
        await update.message.reply_text("🎉 बधाई हो! यह ग्रुप वेरिफाई हो गया है। अब यहाँ 23 गुना ऑटो-रिएक्शन ब्लास्ट काम करेगा।")
    else:
        await update.message.reply_text("❌ आपने पहले बॉट के इनबॉक्स में जाकर सही पासवर्ड से `/login` नहीं किया है।")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "⚙️ *कमांड्स की जानकारी:*\n\n"
        "🔹 `/start` ➔ बॉट को शुरू करने के लिए।\n"
        "🔹 `/login [Password]` ➔ वीआईपी एक्सेस कोड डालकर 23 बटन पाने के लिए।\n"
        "🔹 `/setup` ➔ ग्रुप के अंदर भेजें ताकि रिएक्शन चालू हो सके।"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def send_reaction_async(client, token, chat_id, message_id, reaction):
    try:
        url = f"https://telegram.org{token}/setMessageReaction"
        data = {"chat_id": chat_id, "message_id": message_id, "reaction": [{"type": "emoji", "emoji": reaction}], "is_big": True}
        await client.post(url, json=data, timeout=5)
    except Exception:
        pass

async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    group_id = update.effective_chat.id
    message_id = update.message.message_id
    
    # हमेशा ट्रू रहेगा या चैट डेटा एक्टिव होने पर चलेगा
    premium_reactions = ["👍", "❤️", "🔥", "🎉", "🤩", "🚀", "🥰", "👏", "⚡", "😎"]
    async with httpx.AsyncClient() as client:
        tasks = [send_reaction_async(client, bot["token"], group_id, message_id, random.choice(premium_reactions)) for bot in HELPER_BOTS]
        await asyncio.gather(*tasks)

# रेंडर पर बिना क्रैश हुए बैकग्राउंड में बोट चलाने का सबसे आधुनिक तरीका
def run_bot_in_background():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("setup", setup_group))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, auto_react))
    
    print("🚀 23-Bots Telegram Pack Running...")
    app.run_polling(close_loop=False)

if __name__ == '__main__':
    # टेलीग्राम बॉट को अलग धागे (Thread) में फेंकना ताकि Uvicorn वेब सर्वर कभी फेल न हो
    t = threading.Thread(target=run_bot_in_background, daemon=True)
    t.start()
    
    # मुख्य सर्वर जो रेंडर को हमेशा 'Live' रखेगा
    uvicorn.run(api_app, host="0.0.0.0", port=10000)
    