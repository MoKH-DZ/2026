import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Application, CommandHandler
import asyncio
import nest_asyncio
import time
import threading
from flask import Flask

# ===== إعدادات البوت =====
TOKEN = "8049690165:AAEYWPJzpggMfwEXykjG-ybYFc8poRtY9_0"
CHAT_ID = 5686817749  # ضع ID الخاص بك من @userinfobot
SEARCH_TERMS = [
    "Transporter", "Multivan", "Transporteur", "Caravelle", "Kombi",
    "طروسبورتار", "ميلتيفان", "T5", "T6", "T6.1", "طرانسبورتاو", "golf"
]
BASE_URL = "https://www.ouedkniss.com/automobiles_vehicules/1?keywords={}"

# تخزين الإعلانات المرسلة
seen_ads = set()

# إصلاح مشكلة event loop في Replit
nest_asyncio.apply()

# تهيئة البوت
bot = Bot(token=TOKEN)

# ===== Flask لإبقاء Replit شغال =====
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is running"

def run_web():
    app_web.run(host='0.0.0.0', port=8080)

# ===== دالة جلب الإعلانات =====
def fetch_ads():
    """جلب الإعلانات الجديدة التي نزلت منذ دقائق"""
    new_ads = []
    for term in SEARCH_TERMS:
        url = BASE_URL.format(term)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.find_all("a", href=True):
            title = item.get_text(strip=True)
            href = item["href"]

            # شرط: الإعلان جديد ("il y a" أو "منذ" في النص)
            if any(keyword in title.lower() for keyword in ["il y a", "منذ"]):
                full_url = "https://www.ouedkniss.com" + href
                if full_url not in seen_ads:
                    seen_ads.add(full_url)
                    new_ads.append(full_url)
    return new_ads

# ===== دالة التحقق و الإرسال =====
def check_and_notify():
    while True:
        ads = fetch_ads()
        for ad in ads:
            asyncio.run(bot.send_message(chat_id=CHAT_ID, text=f"🚗 إعلان جديد:\n{ad}"))
        time.sleep(300)  # كل 5 دقائق

# ===== أوامر التيلغرام =====
async def start(update, context):
    await update.message.reply_text("✅ البوت يعمل وسينبهك عند وجود إعلان جديد.")

# ===== Main =====
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # تشغيل فحص الإعلانات في Thread منفصل
    threading.Thread(target=check_and_notify, daemon=True).start()

    # تشغيل Flask في Thread آخر
    threading.Thread(target=run_web, daemon=True).start()

    print("🚀 البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
