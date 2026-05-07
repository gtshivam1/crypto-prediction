# 🤖 Crypto AI Prediction Dashboard

An AI-powered cryptocurrency prediction system that combines Machine Learning, 
Technical Analysis, News Sentiment and Real-time Alerts to predict next day 
prices for the top 5 cryptocurrencies.

---

## 🚀 Live Demo
[Click here to view the dashboard](#) ← replace with your Streamlit link

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
Technical Indicators (RSI, MACD, BB)
        ↓
Random Forest ML Model
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
| Scikit-learn | Random Forest ML model |
| pandas-ta | Technical indicators |
| PostgreSQL | Data storage |
| Streamlit | Interactive dashboard |
| Telegram Bot API | Real-time alerts |

---

## 📁 Project Structure

```
crypto-prediction/
├── extract_prices.py    # Fetches 365 days of historical prices
├── extract_news.py      # Fetches latest crypto news
├── sentiment.py         # VADER sentiment scoring
├── transform.py         # Loads prices into database
├── model.py             # Random Forest prediction model
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
DB_URL=postgresql://postgres:yourpassword@localhost/crypto_prediction
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

**5. Create PostgreSQL database**
```sql
CREATE DATABASE crypto_prediction;
```

**6. Run the pipeline**
```bash
python transform.py       # Load historical prices
python sentiment.py       # Analyze news sentiment
python model.py           # Train model & save predictions
```

**7. Start the dashboard**
```bash
streamlit run dashboard.py
```

**8. Start Telegram alerts (optional)**
```bash
python event_detector.py
```

---

## 📈 Features Explained

### 🔮 Price Prediction
Uses Random Forest Regressor trained on 365 days of data with 17 features
including previous prices, moving averages, technical indicators and sentiment.

### 📰 Sentiment Analysis
Fetches latest news for each coin and scores each headline using VADER
(Valence Aware Dictionary and sEntiment Reasoner) which is specifically
designed for financial and social media text.

### 📊 Technical Indicators
- **RSI** — Identifies overbought (>70) or oversold (<30) conditions
- **MACD** — Shows momentum and trend direction
- **Bollinger Bands** — Shows price volatility range

### 🚨 Alert System
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
**SHiVAM**
- GitHub: [@gtshivam1](https://github.com/gtshivam1)

---

## 🤝 Built With Help From
This project was built with guidance from **[Claude](https://claude.ai)** by Anthropic —
an AI assistant that helped with code, debugging, and project architecture.