# bot.py - मुख्य फ़ाइल जो पूरे आर्किटेक्चर को एक साथ चलाती है

import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client
import config
from reaction_engine import start_reaction_engine

# 1. रेंडर सर्वर को ज़िंदा रखने के लिए FLASK WEB SERVER सेटअप
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    # रेंडर का स्टेटस चेक करने के लिए (https://auto-reaction-bot-ayqv.onrender.com)
    return "✅ Central Reaction Bot Server is Live and Healthy!", 200

@flask_app.route('/telegram', methods=['POST'])
def telegram_webhook():
    # आपके टेलीग्राम लाइव वेबहुक एंडपॉइंट के लिए
    return "OK", 200

def run_flask_server():
    # रेंडर द्वारा दिए गए डायनामिक पोर्ट को बाइंड करना
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# 2. मेन कंट्रोलर बॉट क्लाइंट (यह आपके हैंडलर फ़ाइलों के प्लगइन्स को ऑटो-लोड करेगा)
main_bot = Client(
    "MainControlBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root=".") # यह admin_handlers और user_handlers को खुद ढूंढ लेगा
)

async def main():
    # अ) फ्लैस्क सर्वर को बैकग्राउंड थ्रेड में चालू करना
    flask_thread = threading.Thread(target=run_flask_server)
    flask_thread.daemon = True
    flask_thread.start()
    print("🌐 Flask Web Server successfully bound to Render Port.")

    # ब) दोनों इंजनों को एक साथ एसिंक्रोनस तरीके से चालू करना
    print("🤖 Launching Main Admin Bot...")
    await main_bot.start()
    
    print("⚡ Launching 23x Reaction Worker Engine...")
    await start_reaction_engine()
    
    # स) बॉट को चालू रखना जब तक आप खुद बंद न करें
    print("🚀 System Setup Complete. Enterprise Bot Business is now ONLINE!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    # पायथन के एसिंक्रोनस लूप को रन करना
    asyncio.run(main())
    