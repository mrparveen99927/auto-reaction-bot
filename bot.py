import logging
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from database import generate_user_credentials, login_and_lock_group, is_group_allowed, get_all_active_users

BOT_TOKEN = "8843244865:AAGS47kvrD-ZeOTr-EgxSYFoYY-Cg3SJk-A"
ADMIN_ID = 1780858471  

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running 24/7!")

def run_health_server():
    try:
        server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
        server.serve_forever()
    except Exception as e:
        print(f"Server Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type
    if chat_type == "private":
        await update.message.reply_text(
            "👋 नमस्ते! इस ऑटो-रिएक्शन बॉट का उपयोग करने के लिए लॉगिन करें।\n\n"
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
            await update.message.reply_text(
                f"✅ ग्राहक क्रेडेंशियल सफलतापूर्वक सेट हो गया है!\n\n"
                f"🔑 ID: `{access_id}`\n"
                f"🔒 Pass: `{password}`\n"
                f"⏳ वैधता: {days} दिन"
            )
        else:
            await update.message.reply_text("❌ क्रेडेंशियल सेट करने में कोई त्रुटि हुई।")
    except IndexError:
        await update.message.reply_text("❌ सही तरीका: `/gen_user [ID] [Password] [Days]`")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type
    if chat_type != "private":
        return

    try:
        access_id = context.args[0]
        password = context.args[1]
        
        context.user_data['access_id'] = access_id
        context.user_data['password'] = password
        
        await update.message.reply_text(
            "🔑 क्रेडेंशियल दर्ज कर लिए गए हैं।\n\n"
            "अब इस बॉट को अपने **ग्रुप में एडमिन** बनाएं और ग्रुप चैट में जाकर यह कमांड भेजें:\n"
            "`/setup`"
        )
    except IndexError:
        await update.message.reply_text("❌ सही तरीका: `/login [ID] [Password]`")

async def setup_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type
    if chat_type not in ["group", "supergroup"]:
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
        await update.message.reply_text("🎉 बधाई हो! यह ग्रुप इस आईडी के साथ हमेशा के लिए लॉक हो गया है। अब यहाँ ऑटो-रिएक्शन काम करेगा।")
    elif status == "invalid":
        await update.message.reply_text("❌ गलत ID या पासवर्ड।")
    elif status == "expired":
        await update.message.reply_text("⏳ आपका प्लान समाप्त हो चुका है।")
    elif status == "group_already_used":
        await update.message.reply_text("❌ यह ग्रुप पहले से ही किसी अन्य ID के साथ लिंक है।")
    elif status == "wrong_group":
        await update.message.reply_text("❌ यह ID केवल आपके पहले से लॉक किए गए ग्रुप में ही उपयोग की जा सकती है।")

# एडमिन के लिए सभी एक्टिव ग्राहकों की लिस्ट देखने का नया कमांड
async def all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    users = get_all_active_users()
    if not users:
        await update.message.reply_text("👥 अभी कोई भी एक्टिव ग्राहक मौजूद नहीं है।")
        return

    response = "📋 *एक्टिव ग्राहकों की सूची:*\n\n"
    for u in users:
        response += (
            f"👤 *ID:* `{u['id']}`\n"
            f"🔒 *Pass:* `{u['pass']}`\n"
            f"⏳ *बचा हुआ समय:* {u['time']}\n"
            f"📢 *Group ID:* `{u['group']}`\n"
            f"───────────────────\n"
        )
    await update.message.reply_text(response, parse_mode="Markdown")

# सभी कमांड्स की लिस्ट देखने का नया कमांड (Help)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id == ADMIN_ID:
        admin_help = (
            "🛠️ *मालिक (Admin) कमांड्स की सूची:*\n\n"
            "🔹 `/gen_user [ID] [Pass] [Days]` \n"
            "➔ नया ग्राहक बनाने या पुराने ग्राहक को रिन्यू करने के लिए।\n\n"
            "🔹 `/all_users` \n"
            "➔ सभी एक्टिव ग्राहकों की ID, पासवर्ड और बचे हुए दिनों की लिस्ट देखने के लिए।\n\n"
            "🔹 `/help` \n"
            "➔ यह कमांड गाइड देखने के लिए।"
        )
        await update.message.reply_text(admin_help, parse_mode="Markdown")
    else:
        user_help = (
            "⚙️ *ग्राहक (User) कमांड्स की सूची:*\n\n"
            "🔹 `/start` \n"
            "➔ बॉट को शुरू करने और बेसिक जानकारी के लिए।\n\n"
            "🔹 `/login [ID] [Pass]` \n"
            "➔ बॉट के इनबॉक्स में अपना क्रेडेंशियल डालकर लॉगिन करने के लिए।\n\n"
            "🔹 `/setup` \n"
            "➔ बॉट को अपने ग्रुप में एडमिन बनाकर, ग्रुप के अंदर यह कमांड चलाएं ताकि ग्रुप लॉक हो सके।\n\n"
            "🔹 `/help` \n"
            "➔ कमांड्स की जानकारी के लिए।"
        )
        await update.message.reply_text(user_help, parse_mode="Markdown")

async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    group_id = update.effective_chat.id
    if is_group_allowed(group_id):
        try:
            premium_reactions = ["👍", "❤️", "🔥", "🎉", "🤩", "🚀", "🥰", "👏", "⚡", "😎"]
            chosen_reaction = random.choice(premium_reactions)
            await update.message.set_reaction(reaction=chosen_reaction)
        except Exception as e:
            print(f"Reaction Error: {e}")

def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen_user", gen_user))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("setup", setup_group))
    app.add_handler(CommandHandler("all_users", all_users))
    app.add_handler(CommandHandler("help", help_command))
    
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, auto_react))

    print("🚀 बॉट चालू हो रहा है...")
    app.run_polling()

if __name__ == '__main__':
    main()
    