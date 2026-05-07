import requests
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

COINS = {
    "bitcoin":     "Bitcoin BTC crypto",
    "ethereum":    "Ethereum ETH crypto",
    "binancecoin": "BNB Binance crypto",
    "ripple":      "XRP Ripple crypto",
    "solana":      "Solana SOL crypto"
}

def extract_news():
    all_news = []
    for coin_id, query in COINS.items():
        print(f"Fetching news for {coin_id}...")
        url = "https://newsapi.org/v2/everything"
        params = {
            "q":        query,
            "language": "en",
            "sortBy":   "publishedAt",
            "pageSize": 100,
            "apiKey":   NEWS_API_KEY
        }
        response = requests.get(url, params=params)
        articles = response.json().get("articles", [])

        for article in articles:
            all_news.append({
                "coin_id":      coin_id,
                "headline":     article["title"],
                "description":  article["description"],
                "published_at": article["publishedAt"],
                "source":       article["source"]["name"]
            })

    df = pd.DataFrame(all_news)
    print(f"✅ Extracted {len(df)} news articles!")
    return df

if __name__ == "__main__":
    df = extract_news()
    print(df.head())