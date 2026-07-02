# config.py - क्रेडेंशियल्स और कॉन्फ़िगरेशन फ़ाइल

import os

# --- MAIN BOT & ADMIN SETTINGS ---
# आपका मेन बॉट टोकन जिससे यूज़र लॉगिन करेंगे
BOT_TOKEN = "8843244865:AAGS47kvrD-ZeOTr-EgxSYFoYY-Cg3SJk-A"

# आपकी असली टेलीग्राम ID ताकि एडमिन कमांड्स सिर्फ आपके अकाउंट से चलें
ADMIN_ID = 1780858471

# Pyrogram के लिए बुनियादी क्रेडेंशियल्स (आप my.telegram.org से भी बदल सकते हैं)
API_ID = 123456
API_HASH = "your_api_hash_here"

# --- DATABASE SETTINGS ---
# आपकी लाइव MongoDB कनेक्शन स्ट्रिंग जो डेटाबेस को जोड़ेगी
MONGO_URI = "mongodb+srv://arena_user:Arena999@cluster0.pluvfcd.mongodb.net/central_wallet_db?appName=Cluster0"
DB_NAME = "reaction_bot_db"
COLLECTION_NAME = "reaction_vip_users"

# --- 23 HELPER BOTS TOKENS ---
# यहाँ आपको अपने सभी 23 हेल्पर्स बॉट्स के टोकन कॉमा (,) लगाकर डालने हैं
HELPER_TOKENS = [
    "TOKEN_BOT_1", "TOKEN_BOT_2", "TOKEN_BOT_3", "TOKEN_BOT_4", "TOKEN_BOT_5",
    "TOKEN_BOT_6", "TOKEN_BOT_7", "TOKEN_BOT_8", "TOKEN_BOT_9", "TOKEN_BOT_10",
    "TOKEN_BOT_11", "TOKEN_BOT_12", "TOKEN_BOT_13", "TOKEN_BOT_14", "TOKEN_BOT_15",
    "TOKEN_BOT_16", "TOKEN_BOT_17", "TOKEN_BOT_18", "TOKEN_BOT_19", "TOKEN_BOT_20",
    "TOKEN_BOT_21", "TOKEN_BOT_22", "TOKEN_BOT_23"
]

# ऑटोमैटिक रिएक्शंस की लिस्ट जो रैंडमली पोस्ट पर जाएगी
REACTIONS_POOL = ["👍", "🔥", "❤️", "🥰", "👏", "🎉", "🤩", "🚀", "⚡"]
