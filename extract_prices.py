import requests
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("COINGECKO_API_KEY")

COINS = {
    "bitcoin":  {"name": "Bitcoin",  "symbol": "BTC"},
    "ethereum": {"name": "Ethereum", "symbol": "ETH"},
    "binancecoin": {"name": "BNB",   "symbol": "BNB"},
    "ripple":   {"name": "XRP",      "symbol": "XRP"},
    "solana":   {"name": "Solana",   "symbol": "SOL"}
}

def extract_historical_prices(days=365):
    all_data = []
    for coin_id, info in COINS.items():
        print(f"Fetching {info['name']} historical data...")
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "daily",
            "x_cg_demo_api_key": API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()

        prices = data["prices"]
        volumes = data["total_volumes"]
        market_caps = data["market_caps"]

        for i in range(len(prices)):
            timestamp = prices[i][0] / 1000
            date = datetime.utcfromtimestamp(timestamp).date()
            all_data.append({
                "coin_id":     coin_id,
                "name":        info["name"],
                "symbol":      info["symbol"],
                "date":        date,
                "price":       prices[i][1],
                "total_volume": volumes[i][1],
                "market_cap":  market_caps[i][1]
            })

    df = pd.DataFrame(all_data)
    print(f"✅ Extracted {len(df)} rows of historical data!")
    return df

if __name__ == "__main__":
    df = extract_historical_prices()
    print(df.head())