# 🤖 Crypto AI Prediction Dashboard

An AI-powered cryptocurrency prediction system that combines Machine Learning, Technical Analysis, News Sentiment and Real-time Alerts to predict next day prices for the top 5 cryptocurrencies by market cap.

---

## 🚀 Live Demo
[Click here to view the dashboard](https://cryptopredictionxyz.streamlit.app)

---

## 📊 What it does

- 🔮 Predicts tomorrow's price for BTC, ETH, BNB, XRP and SOL
- 📰 Analyzes news sentiment using VADER AI scoring
- 📈 Uses technical indicators — RSI, MACD and Bollinger Bands
- 🚨 Sends real-time Telegram alerts for major market events
- 📊 Displays everything on an interactive dark themed Streamlit dashboard
- ☁️ Stores all data on Supabase cloud database

---

## 🧠 How the Prediction Works

```
Historical Prices (365 days from CoinGecko)
            +
News Sentiment Score (VADER AI)
            +
Technical Indicators (RSI, MACD, Bollinger Bands)
            ↓
XGBoost ML Model trained on 17 features
            ↓
Tomorrow's Predicted Price + Change %
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| CoinGecko API | Historical and live crypto prices |
| NewsAPI | Latest crypto news articles |
| VADER | Financial news sentiment analysis |
| XGBoost | ML prediction model |
| ta | Technical indicators library |
| Supabase | Cloud PostgreSQL database |
| Streamlit | Interactive web dashboard |
| Telegram Bot API | Real-time market alerts |
| SQLAlchemy | Database connection |
| Pandas | Data transformation |

---

## 🤖 Why XGBoost?

We started with Linear Regression, upgraded to Random Forest and finally settled on XGBoost because:
- ⚡ Fastest training speed
- 🎯 Most accurate predictions (lowest MAE)
- 🛡️ Best handling of overfitting
- 💼 Most widely used model in professional trading firms

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
| prev_price | Yesterday's closing price |
| prev_price_2 | Price 2 days ago |
| prev_price_3 | Price 3 days ago |
| price_change | Daily percentage change |
| ma7 | 7 day moving average |
| ma30 | 30 day moving average |
| ma7_ma30_diff | Gap between MA7 and MA30 |
| volatility | 7 day price volatility |
| volume_change | Trading volume % change |
| rsi | Relative Strength Index |
| macd | MACD line |
| macd_signal | MACD signal line |
| macd_diff | MACD histogram |
| bb_upper | Bollinger Band upper limit |
| bb_lower | Bollinger Band lower limit |
| bb_width | Bollinger Band width |
| sentiment | VADER news sentiment score |

---

## 🗄️ Database — Supabase

All data is stored on **Supabase** — a free cloud PostgreSQL database with 3 tables:

- **historical_prices** — 1830 rows of 365 days price data for 5 coins
- **news_sentiment** — 100 news articles with VADER sentiment scores
- **predictions** — daily XGBoost predictions saved automatically

---

## 📁 Project Structure

```
crypto-prediction/
├── extract_prices.py    # Fetches 365 days of historical prices from CoinGecko
├── extract_news.py      # Fetches latest crypto news from NewsAPI
├── sentiment.py         # VADER sentiment scoring and database load
├── transform.py         # Transforms and loads prices into Supabase
├── model.py             # XGBoost prediction model with 17 features
├── event_detector.py    # Real-time Telegram alert bot (runs every 15 mins)
├── dashboard.py         # Dark themed Streamlit dashboard
├── requirements.txt     # All project dependencies
└── .env                 # API keys (not included in repo)
```

---

## ⚙️ Setup Instructions

**1. Clone the repository**
```bash
git clone https://github.com/gtshivam1/crypto-prediction.git
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
python transform.py       # Load 365 days of historical prices
python sentiment.py       # Fetch news and analyze sentiment
python model.py           # Train XGBoost and save predictions
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

## 🚨 Real-time Alert System

The alert bot scans news every 15 minutes and sends instant Telegram notifications for:
- 🚨 Critical events — hacks, exchange breaches, bans, fraud
- ⚠️ Major events — SEC actions, government regulations, lawsuits
- 🚀 Bullish events — ETF approvals, partnerships, all time highs

---

## ⚠️ Disclaimer
This project is for educational purposes only. Cryptocurrency predictions are not financial advice. Crypto markets are highly volatile — always do your own research before investing.

---

## 👨‍💻 Author
**SHiVAM**
- GitHub: [@gtshivam1](https://github.com/gtshivam1)


---

## 🤝 Built With Help From
This project was built with guidance from [Claude](https://claude.ai) by Anthropic — an AI assistant that helped with architecture, code, debugging and project structure.