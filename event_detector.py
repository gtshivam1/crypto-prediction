import requests
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
NEWS_API_KEY    = os.getenv("NEWS_API_KEY")
TELEGRAM_TOKEN  = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Keywords that trigger alerts
CRITICAL_KEYWORDS = [
    "hack", "exploit", "breach", "stolen", "attack",
    "ban", "illegal", "shutdown", "arrest", "fraud"
]

MAJOR_KEYWORDS = [
    "regulation", "sec", "lawsuit", "investigation",
    "elon musk", "trump", "government", "federal"
]

BULLISH_KEYWORDS = [
    "etf approved", "adoption", "partnership", "upgrade",
    "all time high", "rally", "bullish", "surge", "moon"
]

COINS = ["bitcoin", "ethereum", "BNB", "XRP", "solana"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

def get_severity(headline):
    headline_lower = headline.lower()
    if any(kw in headline_lower for kw in CRITICAL_KEYWORDS):
        return "🚨 CRITICAL", -0.8
    elif any(kw in headline_lower for kw in MAJOR_KEYWORDS):
        return "⚠️ MAJOR", -0.4
    elif any(kw in headline_lower for kw in BULLISH_KEYWORDS):
        return "🚀 BULLISH", +0.8
    return None, 0

def detect_events():
    print(f"🔍 Scanning news at {datetime.now().strftime('%H:%M:%S')}...")
    alerts_sent = 0

    for coin in COINS:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q":        f"{coin} crypto",
            "language": "en",
            "sortBy":   "publishedAt",
            "pageSize": 5,
            "apiKey":   NEWS_API_KEY
        }
        response = requests.get(url, params=params)
        articles = response.json().get("articles", [])

        for article in articles:
            headline = article.get("title", "")
            severity, impact = get_severity(headline)

            if severity:
                direction = "📉 PRICE MAY DROP" if impact < 0 else "📈 PRICE MAY RISE"
                message = f"""
<b>{severity} ALERT — {coin.upper()}</b>

📰 <b>Headline:</b> {headline}

{direction}
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔗 <b>Source:</b> {article.get('source', {}).get('name', 'Unknown')}
                """
                send_telegram(message)
                print(f"✅ Alert sent for {coin}: {severity}")
                alerts_sent += 1

    if alerts_sent == 0:
        print("✅ No major events detected")
    
    return alerts_sent

if __name__ == "__main__":
    print("🚀 Event Detector Started!")
    send_telegram("🤖 <b>Crypto Alert Bot is now LIVE!</b>\nMonitoring top 5 coins for major events...")
    
    while True:
        detect_events()
        print("⏳ Waiting 15 minutes before next scan...")
        time.sleep(900)  # scan every 15 minutes