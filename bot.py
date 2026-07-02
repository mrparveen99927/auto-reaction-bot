# bot.py - एरर फ्री अपडेटेड मुख्य फ़ाइल

import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client
import config

# रेंडर सर्वर को ज़िंदा रखने के लिए FLASK WEB SERVER सेटअप
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "✅ Central Reaction Bot Server is Live and Healthy!", 200

@flask_app.route('/telegram', methods=['POST'])
def telegram_webhook():
    return "OK", 200

def run_flask_server():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# मेन कंट्रोलर बॉट क्लाइंट
main_bot = Client(
    "MainControlBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

async def main():
    # 1. फ्लैस्क सर्वर को बैकग्राउंड थ्रेड में चालू करना
    flask_thread = threading.Thread(target=run_flask_server)
    flask_thread.daemon = True
    flask_thread.start()
    print("🌐 Flask Web Server successfully bound to Render Port.")

    # 2. कोड चलने से पहले हैंडलर्स को मैन्युअली लोड करना (ताकि प्लगइन एरर न आए)
    import admin_handlers
    import user_handlers
    from reaction_engine import start_reaction_engine

    # 3. दोनों इंजनों को एक साथ चालू करना
    print("🤖 Launching Main Admin Bot...")
    await main_bot.start()
    
    print("⚡ Launching 23x Reaction Worker Engine...")
    await start_reaction_engine()
    
    print("🚀 System Setup Complete. Enterprise Bot Business is now ONLINE!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
    