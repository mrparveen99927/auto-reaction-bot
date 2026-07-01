import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from database import generate_user_credentials, login_and_lock_group, is_group_allowed

# आपका Telegram Bot Token जो BotFather से मिला था
BOT_TOKEN = "8843244865:AAGS47kvrD-ZeOTr-EgxSYFoYY-Cg3SJk-A"

# आपकी असली Telegram Chat ID (अब यह पूरी तरह सेट है)
ADMIN_ID = 1780858471  

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

# /start कमांड का जवाब
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type
    if chat_type == "private":
        await update.message.reply_text(
            "👋 नमस्ते! इस ऑटो-रिएक्शन बॉट का उपयोग करने के लिए लॉगिन करें।\n\n"
            "👉 लॉगिन करने के लिए इस तरह मैसेज भेजें:\n"
            "`/login [Access_ID] [Password]`\n\n"
            "उदाहरण: `/login user123 pass456`"
        )

# एडमिन कमांड: नया ग्राहक आईडी और पासवर्ड जनरेट करना
async def gen_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return  # सिर्फ आपके लिए (मालिक)

    try:
        access_id = context.args[0]
        password = context.args[1]
        days = int(context.args[2]) if len(context.args) > 2 else 30
        
        success = generate_user_credentials(access_id, password, days)
        if success:
            await update.message.reply_text(
                f"✅ नया ग्राहक क्रेडेंशियल जनरेट हो गया है!\n\n"
                f"🔑 ID: `{access_id}`\n"
                f"🔒 Pass: `{password}`\n"
                f"⏳ वैधता: {days} दिन\n\n"
                f"यह विवरण अपने कस्टमर को दे दें।"
            )
        else:
            await update.message.reply_text("❌ यह Access ID पहले से मौजूद है। कृपया दूसरी चुनें।")
    except IndexError:
        await update.message.reply_text("❌ सही तरीका: `/gen_user [ID] [Password] [Days]`")

# ग्राहक के लिए लॉगिन प्रोसेस
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type
    if chat_type != "private":
        return

    try:
        access_id = context.args[0]
        password = context.args[1]
        
        # यूज़र का डेटा थोड़े समय के लिए मेमोरी में सेव करना
        context.user_data['access_id'] = access_id
        context.user_data['password'] = password
        
        await update.message.reply_text(
            "🔑 क्रेडेंशियल दर्ज कर लिए गए हैं।\n\n"
            "अब इस बॉट को अपने उस **ग्रुप में एडमिन** बनाएं जहां आप ऑटो-रिएक्शन चाहते हैं।\n"
            "ग्रुप में एडमिन बनाने के बाद, ग्रुप चैट में जाकर यह कमांड भेजें:\n"
            "`/setup`"
        )
    except IndexError:
        await update.message.reply_text("❌ सही तरीका: `/login [ID] [Password]`")

# ग्रुप में बॉट को लॉक (Setup) करने का कमांड
async def setup_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type
    if chat_type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ यह कमांड केवल ग्रुप के अंदर काम करेगी।")
        return

    access_id = context.user_data.get('access_id')
    password = context.user_data.get('password')

    if not access_id or not password:
        await update.message.reply_text("❌ आपने पहले बॉट के इनबॉक्स (DM) में जाकर `/login` नहीं किया है। पहले वहां लॉगिन करें।")
        return

    group_id = update.effective_chat.id
    
    # डेटाबेस में ग्रुप लॉक चेक करना
    status = login_and_lock_group(access_id, password, group_id)
    
    if status == "success":
        await update.message.reply_text("🎉 बधाई हो! यह ग्रुप इस आईडी के साथ हमेशा के लिए लॉक हो गया है। अब इस ग्रुप की पोस्ट्स पर ऑटो-रिएक्शन काम करेगा।")
    elif status == "invalid":
        await update.message.reply_text("❌ गलत ID या पासवर्ड। कृपया दोबारा जांचें।")
    elif status == "expired":
        await update.message.reply_text("⏳ आपका प्लान समाप्त हो चुका है। कृपया एडमिन से संपर्क करें।")
    elif status == "group_already_used":
        await update.message.reply_text("❌ यह ग्रुप पहले से ही किसी अन्य ID के साथ लिंक है।")
    elif status == "wrong_group":
        await update.message.reply_text("❌ यह ID केवल आपके पहले से लॉक किए गए ग्रुप में ही उपयोग की जा सकती है।")

# मुख्य ऑटो-रिएक्शन लॉजिक
async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    group_id = update.effective_chat.id
    
    # चेक करें कि क्या यह ग्रुप किसी एक्टिव पेड ग्राहक का है
    if is_group_allowed(group_id):
        try:
            # यहाँ डिफ़ॉल्ट रूप से थम्स अप '👍' रिएक्शन जाएगा
            await update.message.set_reaction(reaction="👍")
        except Exception as e:
            print(f"Reaction Error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen_user", gen_user))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("setup", setup_group))
    
    # ग्रुप के सभी नए मैसेजेस को ट्रैक करने के लिए
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, auto_react))

    print("🚀 बॉट चालू हो रहा है...")
    app.run_polling()

if __name__ == '__main__':
    main()
    