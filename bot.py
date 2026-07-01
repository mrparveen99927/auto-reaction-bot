import logging
import random
import asyncio
import httpx
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

BOT_TOKEN = "8843244865:AAGS47kvrD-ZeOTr-EgxSYFoYY-Cg3SJk-A"
ADMIN_ID = 1780858471  
VIP_PASSWORD = "PREMIUM_VIP_2026"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

# FastAPI ऐप जो रेंडर पर हमेशा वेबसाइट की तरह लाइव रहेगा
api_app = FastAPI()
bot_app = Application.builder().token(BOT_TOKEN).build()

# सभी 23 बॉट्स की लिस्ट
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

@api_app.get("/")
def read_root():
    return {"status": "VIP 23-Bots Webhook Engine is Online 24/7"}

# टेलीग्राम से मैसेज रिसीव करने का वेबहुक रूट
@api_app.post("/telegram")
async def telegram_webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}

async def start(update: Update, context):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "👋 नमस्ते! वीआईपी 23× मल्टी-ऑटो-रिएक्शन सर्विस चालू है।\n\n"
            "👉 लॉगिन करने के लिए अपना पासवर्ड इस तरह भेजें:\n"
            "`/login आपका_पासवर्ड`"
        )

async def login(update: Update, context):
    if update.effective_chat.type != "private":
        return
    try:
        user_password = context.args[0]
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

async def setup_group(update: Update, context):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ यह कमांड केवल ग्रुप के अंदर काम करेगी।")
        return
    if context.user_data.get('is_vip') or update.effective_user.id == ADMIN_ID:
        context.chat_data['active'] = True
        await update.message.reply_text("🎉 बधाई हो! यह ग्रुप वेरिफाई हो गया है। अब यहाँ 23 गुना ऑटो-रिएक्शन ब्लास्ट काम करेगा।")
    else:
        await update.message.reply_text("❌ आपने पहले बॉट के इनबॉक्स में जाकर सही पासवर्ड से `/login` नहीं किया है।")

async def help_command(update: Update, context):
    help_text = (
        "⚙️ *कमांड्स की जानकारी:*\n\n"
        "🔹 `/start` ➔ बॉट को शुरू करने के लिए।\n"
        "🔹 `/login [Password]` ➔ 23 बटन पाने के लिए।\n"
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

async def auto_react(update: Update, context):
    if not update.message:
        return
    group_id = update.effective_chat.id
    message_id = update.message.message_id
    premium_reactions = ["👍", "❤️", "🔥", "🎉", "🤩", "🚀", "🥰", "👏", "⚡", "😎"]
    async with httpx.AsyncClient() as client:
        tasks = [send_reaction_async(client, bot["token"], group_id, message_id, random.choice(premium_reactions)) for bot in HELPER_BOTS]
        await asyncio.gather(*tasks)

# यह फंक्शन बॉट चालू होते ही अपने आप टेलीग्राम को आपका रेंडर लिंक बता देगा
@api_app.on_event("startup")
async def on_startup():
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("login", login))
    bot_app.add_handler(CommandHandler("setup", setup_group))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, auto_react))
    
    await bot_app.initialize()
    await bot_app.start()
    
    # 🔥 जादू की लाइन: यहाँ आपका रेंडर लिंक अपने आप टेलीग्राम पर सेट हो जाएगा
    your_render_url = "https://auto-reaction-bot-ayqv.onrender.com"
    await bot_app.bot.set_webhook(url=your_render_url)
    logging.info(f"🚀 Webhook automatically set to: {your_render_url}")
    