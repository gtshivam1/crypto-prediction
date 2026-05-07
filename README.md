# 🤖 Crypto AI Prediction Dashboard

An AI-powered cryptocurrency prediction system that combines Machine Learning,
Technical Analysis, News Sentiment and Real-time Alerts to predict next day
prices for the top 5 cryptocurrencies.

---

## 🚀 Live Demo
[Click here to view the dashboard](https://cryptopredictionxyz.streamlit.app)

---

## 📊 What it does

- 🔮 **Predicts tomorrow's price** for BTC, ETH, BNB, XRP, SOL
- 📰 **Analyzes news sentiment** using VADER AI scoring
- 📈 **Technical indicators** — RSI, MACD, Bollinger Bands
- 🚨 **Real-time Telegram alerts** for major market events
- 📊 **Interactive dashboard** built with Streamlit

---

## 🧠 How the Prediction Works

```
Historical Prices (365 days)
        +
News Sentiment Score (VADER)
        +
Technical Indicators (RSI, MACD, Bollinger Bands)
        ↓
XGBoost ML Model (17 features)
        ↓
Tomorrow's Predicted Price
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| CoinGecko API | Historical & live crypto prices |
| NewsAPI | Latest crypto news |
| VADER | News sentiment analysis |
| XGBoost | ML prediction model |
| ta (Technical Analysis) | RSI, MACD, Bollinger Bands |
| PostgreSQL / Supabase | Cloud database |
| Streamlit | Interactive dashboard |
| Telegram Bot API | Real-time alerts |

---

## 🤖 Why XGBoost?

We upgraded from Random Forest to **XGBoost** because:
- ⚡ Faster training
- 🎯 More accurate predictions (lower MAE)
- 🛡️ Better handling of overfitting
- 💼 Used by professional trading firms

### Model Performance (MAE):
| Coin | MAE |
|---|---|
| Bitcoin | $1,767 |
| Ethereum | $108 |
| BNB | $17 |
| XRP | $0.08 |
| Solana | $5.51 |

---

## 📈 17 Features Used by the Model

| Feature | Description |
|---|---|
| prev_price | Yesterday's price |
| prev_price_2 | Price 2 days ago |
| prev_price_3 | Price 3 days ago |
| price_change | Daily % change |
| ma7 | 7 day moving average |
| ma30 | 30 day moving average |
| ma7_ma30_diff | Gap between MA7 and MA30 |
| volatility | 7 day price volatility |
| volume_change | Trading volume change |
| rsi | Relative Strength Index |
| macd | MACD line |
| macd_signal | MACD signal line |
| macd_diff | MACD histogram |
| bb_upper | Bollinger Band upper |
| bb_lower | Bollinger Band lower |
| bb_width | Bollinger Band width |
| sentiment | News sentiment score |

---

## 📁 Project Structure

```
crypto-prediction/
├── extract_prices.py    # Fetches 365 days of historical prices
├── extract_news.py      # Fetches latest crypto news
├── sentiment.py         # VADER sentiment scoring
├── transform.py         # Loads prices into database
├── model.py             # XGBoost prediction model
├── event_detector.py    # Real-time Telegram alert bot
├── dashboard.py         # Streamlit dashboard
├── requirements.txt     # Project dependencies
└── .env                 # API keys (not included)
```

---

## ⚙️ Setup Instructions

**1. Clone the repository**
```bash
git clone https://github.com/YOURUSERNAME/crypto-prediction.git
cd crypto-prediction
```

**2. Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create `.env` file**
```
COINGECKO_API_KEY=your_coingecko_key
NEWS_API_KEY=your_newsapi_key
DB_URL=your_supabase_connection_string
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

**5. Run the pipeline**
```bash
python transform.py       # Load historical prices
python sentiment.py       # Analyze news sentiment
python model.py           # Train model & save predictions
```

**6. Start the dashboard**
```bash
streamlit run dashboard.py
```

**7. Start Telegram alerts**
```bash
python event_detector.py
```

---

## 🚨 Alert System
Monitors news every 15 minutes and sends instant Telegram alerts for:
- 🚨 Critical events (hacks, bans, exploits)
- ⚠️ Major events (regulations, government actions)
- 🚀 Bullish events (ETF approvals, partnerships, rallies)

---

## ⚠️ Disclaimer
This project is for **educational purposes only.**
Cryptocurrency predictions are not financial advice.
Crypto markets are highly volatile — always do your own research.

---

## 👨‍💻 Author
**Your Name**
- GitHub: [@gtshivam1](https://github.com/gtshivam1)


---

## 🤝 Built With Help From
This project was built with guidance from **[Claude](https://claude.ai)** by Anthropic —
an AI assistant that helped with code, debugging, and project architecture.