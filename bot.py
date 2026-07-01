import logging
import random
import asyncio
import httpx
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from database import generate_user_credentials, login_and_lock_group, is_group_allowed, get_all_active_users

BOT_TOKEN = "8843244865:AAGS47kvrD-ZeOTr-EgxSYFoYY-Cg3SJk-A"
ADMIN_ID = 1780858471  

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

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

# टकराव रोकने के लिए लाइफस्पैन इंजन (FastAPI + TG Bot Router)
@asynccontextmanager
async def lifespan(app: FastAPI):
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("gen_user", gen_user))
    bot_app.add_handler(CommandHandler("login", login))
    bot_app.add_handler(CommandHandler("setup", setup_group))
    bot_app.add_handler(CommandHandler("all_users", all_users))
    bot_app.add_handler(CommandHandler("my_plan", my_plan))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, auto_react))
    
    await bot_app.initialize()
    await bot_app.start()
    asyncio.create_task(bot_app.updater.start_polling())
    logging.info("🚀 Telegram Bot Starter Pack Activated inside Lifespan!")
    yield
    await bot_app.updater.stop()
    await bot_app.stop()

api_app = FastAPI(lifespan=lifespan)

@api_app.get("/")
def read_root():
    return {"status": "VIP 23-Bots Engine Running Successfully"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "👋 नमस्ते! इस 23× मल्टी-ऑटो-रिएक्शन वीआईपी बॉट का उपयोग करने के लिए लॉगिन करें।\n\n"
            "👉 लॉगिन करने के लिए इस तरह मैसेज भेजें:\n"
            "`/login [Access_ID] [Password]`\n\n"
            "💡 कमांड्स की पूरी जानकारी के लिए `/help` टाइप करें।"
        )
        async def gen_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        access_id = context.args[0]
        password = context.args[1]
        days = int(context.args[2]) if len(context.args) > 2 else 30
        success = generate_user_credentials(access_id, password, days)
        if success:
            await update.message.reply_text(f"✅ क्रेडेंशियल सेट हो गया है!\n\n🔑 ID: `{access_id}`\n🔒 Pass: `{password}`\n⏳ वैधता: {days} दिन")
        else:
            await update.message.reply_text("❌ क्रेडेंशियल सेट करने में कोई त्रुटि हुई।")
    except IndexError:
        await update.message.reply_text("❌ सही तरीका: `/gen_user [ID] [Password] [Days]`")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    try:
        access_id = context.args[0]
        password = context.args[1]
        context.user_data['access_id'] = access_id
        context.user_data['password'] = password
        
        keyboard = []
        row = []
        for i, bot in enumerate(HELPER_BOTS, start=1):
            link = f"https://t.me{bot['username']}?startgroup=true"
            row.append(InlineKeyboardButton(text=f"➕ बॉट {i}", url=link))
            if len(row) == 2:  # एक लाइन में 2 बटन दिखेंगे ताकि मोबाइल स्क्रीन पर सुंदर लगे
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔑 *क्रेडेंशियल दर्ज कर लिए गए हैं!*\n\n"
            "🔥 अब नीचे दिए गए बटनों पर क्लिक करके सभी 23 बॉट्स को अपने ग्रुप में जोड़ें।\n\n"
            "⚠️ *महत्वपूर्ण:* सभी बॉट्स को शामिल करने के बाद, ग्रुप में जाकर यह कमांड भेजें:\n`/setup`",
            reply_markup=reply_markup, parse_mode="Markdown"
        )
    except IndexError:
        await update.message.reply_text("❌ सही तरीका: `/login [ID] [Password]`")

async def setup_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ यह कमांड केवल ग्रुप के अंदर काम करेगी।")
        return
    access_id = context.user_data.get('access_id')
    password = context.user_data.get('password')
    if not access_id or not password:
        await update.message.reply_text("❌ आपने पहले बॉट के इनबॉक्स (DM) में जाकर `/login` नहीं किया है।")
        return
    group_id = update.effective_chat.id
    status = login_and_lock_group(access_id, password, group_id)
    if status == "success":
        await update.message.reply_text("🎉 बधाई हो! यह ग्रुप लॉक हो गया है। अब यहाँ 23 गुना ऑटो-रिएक्शन ब्लास्ट काम करेगा।")
    else:
        await update.message.reply_text(f"❌ त्रुटि या अमान्य स्थिति: {status}")

async def all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = get_all_active_users()
    if not users:
        await update.message.reply_text("👥 अभी कोई भी एक्टिव ग्राहक मौजूद नहीं है।")
        return
    response = "📋 *एक्टिव ग्राहकों की सूची:*\n\n"
    for u in users:
        response += f"👤 *ID:* `{u['id']}`\n🔒 *Pass:* `{u['pass']}`\n⏳ *समय:* {u['time']}\n📢 *Group:* `{u['group']}`\n───────────────────\n"
    await update.message.reply_text(response, parse_mode="Markdown")

async def my_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_all_active_users()
    access_id = context.user_data.get('access_id', "Guest")
    found_user = None
    for u in users:
        if u['id'] == access_id:
            found_user = u
            break
    if found_user:
        await update.message.reply_text(
            f"📊 *आपके वीआईपी प्लान की जानकारी:*\n\n👤 *Access ID:* `{found_user['id']}`\n⏳ *बचा हुआ समय:* {found_user['time']}\n📢 *ग्रुप आईडी:* `{found_user['group']}`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ कोई एक्टिव प्लान नहीं मिला। पहले `/login` करें।")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        admin_help = (
            "🛠️ *मालिक (Admin) कमांड्स:*\n\n🔹 `/gen_user [ID] [Pass] [Days]` ➔ ग्राहक बनाने/रिन्यू करने के लिए।\n🔹 `/all_users` ➔ एक्टिव ग्राहकों की सूची।\n🔹 `/help` ➔ गाइड।"
        )
        await update.message.reply_text(admin_help, parse_mode="Markdown")
    else:
        user_help = (
            "⚙️ *ग्राहक (User) कमांड्स:*\n\n🔹 `/start` ➔ बेसिक जानकारी।\n🔹 `/login [ID] [Pass]` ➔ 23 बॉट्स के बटन पाने के लिए।\n🔹 `/setup` ➔ ग्रुप के अंदर भेजें।\n🔹 `/my_plan` ➔ प्लान की वैधता देखने के लिए।\n🔹 `/help` ➔ गाइड।"
        )
        await update.message.reply_text(user_help, parse_mode="Markdown")

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
    if is_group_allowed(group_id):
        premium_reactions = ["👍", "❤️", "🔥", "🎉", "🤩", "🚀", "🥰", "👏", "⚡", "😎"]
        async with httpx.AsyncClient() as client:
            tasks = [send_reaction_async(client, bot["token"], group_id, message_id, random.choice(premium_reactions)) for bot in HELPER_BOTS]
            await asyncio.gather(*tasks)

if __name__ == '__main__':
    uvicorn.run("bot:api_app", host="0.0.0.0", port=10000)
    