import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sqlalchemy import create_engine
import ta
import os
from dotenv import load_dotenv
from model import build_model

load_dotenv()
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)

st.set_page_config(
    page_title="CryptoAI Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Dark theme
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
    }
    div[data-testid="stMetricValue"] { color: #e6edf3; }
    .stDataFrame { background-color: #161b22; }
    .stSelectbox label { color: #e6edf3; }
    h1, h2, h3, h4 { color: #e6edf3; }
    .stDivider { border-color: #30363d; }
    .card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }
    .alert-critical { 
        background-color: #3d1a1a; 
        border-left: 4px solid #f85149;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .alert-major { 
        background-color: #2d2a1a;
        border-left: 4px solid #e3b341;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .alert-bullish { 
        background-color: #1a2d1a;
        border-left: 4px solid #3fb950;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Dark matplotlib style
plt.rcParams.update({
    "figure.facecolor":  "#0d1117",
    "axes.facecolor":    "#161b22",
    "axes.edgecolor":    "#30363d",
    "axes.labelcolor":   "#e6edf3",
    "xtick.color":       "#e6edf3",
    "ytick.color":       "#e6edf3",
    "text.color":        "#e6edf3",
    "grid.color":        "#30363d",
    "legend.facecolor":  "#161b22",
    "legend.edgecolor":  "#30363d",
})

# Header
st.markdown("""
<div style="background: linear-gradient(90deg, #1f6feb, #388bfd);
            padding: 25px; border-radius: 12px; margin-bottom: 20px;">
    <h1 style="color:white; margin:0">🤖 CryptoAI Prediction Dashboard</h1>
    <p style="color:#cdd9e5; margin:5px 0 0 0">
        Random Forest ML • Technical Indicators • News Sentiment • Live Alerts
    </p>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_all_data():
    predictions = build_model()
    prices      = pd.read_sql("SELECT * FROM historical_prices", engine)
    sentiment   = pd.read_sql("SELECT * FROM news_sentiment", engine)
    return predictions, prices, sentiment

with st.spinner("🤖 Running AI prediction model..."):
    predictions, prices, sentiment = load_all_data()

# ─── SECTION 1: Predictions ───────────────────────────────────────────────────
st.subheader("🎯 Tomorrow's AI Price Predictions")
cols = st.columns(5)
for i, row in predictions.iterrows():
    arrow  = "📈" if row["change_pct"] > 0 else "📉"
    color  = "#3fb950" if row["change_pct"] > 0 else "#f85149"
    sentiment_label = "😃 Positive" if row["sentiment_score"] > 0.2 else "😨 Negative" if row["sentiment_score"] < -0.2 else "😐 Neutral"
    rsi_label = "🔴 Overbought" if row["rsi"] > 70 else "🟢 Oversold" if row["rsi"] < 30 else "🟡 Neutral"
    cols[i].markdown(f"""
    <div class="card">
        <h4>{arrow} {row['coin_id'].upper()}</h4>
        <h2 style="color:{color}">${row['predicted_price']:,.2f}</h2>
        <p style="color:{color}">{row['change_pct']:+.2f}%</p>
        <hr style="border-color:#30363d">
        <small>Current: ${row['current_price']:,.2f}</small><br>
        <small>RSI: {row['rsi']:.1f} {rsi_label}</small><br>
        <small>Sentiment: {sentiment_label}</small><br>
        <small>MAE: ${row['mae']:,.2f}</small><br>
        <small>Top Signal: {row['top_feature']}</small>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ─── SECTION 2: Coin Analysis ─────────────────────────────────────────────────
st.subheader("🔍 Deep Coin Analysis")
coin = st.selectbox("Select Coin", predictions["coin_id"].tolist())
coin_prices   = prices[prices["coin_id"] == coin].sort_values("date").copy()
coin_sentiment = sentiment[sentiment["coin_id"] == coin]

# Calculate indicators
coin_prices["ma7"]        = coin_prices["price"].rolling(7).mean()
coin_prices["ma30"]       = coin_prices["price"].rolling(30).mean()
coin_prices["rsi"]        = ta.momentum.RSIIndicator(coin_prices["price"], window=14).rsi()
macd_ind                  = ta.trend.MACD(coin_prices["price"])
coin_prices["macd"]       = macd_ind.macd()
coin_prices["macd_signal"]= macd_ind.macd_signal()
coin_prices["macd_diff"]  = macd_ind.macd_diff()
bb                        = ta.volatility.BollingerBands(coin_prices["price"], window=20)
coin_prices["bb_upper"]   = bb.bollinger_hband()
coin_prices["bb_lower"]   = bb.bollinger_lband()
coin_prices               = coin_prices.dropna()

# Last 90 days
recent = coin_prices.tail(90)

col1, col2 = st.columns(2)

with col1:
    # Price + MA + BB chart
    st.markdown("**📈 Price History + Moving Averages + Bollinger Bands**")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(recent["date"], recent["price"],    color="#388bfd", linewidth=2,   label="Price")
    ax.plot(recent["date"], recent["ma7"],      color="#3fb950", linewidth=1.5, label="MA7",   linestyle="--")
    ax.plot(recent["date"], recent["ma30"],     color="#e3b341", linewidth=1.5, label="MA30",  linestyle="--")
    ax.fill_between(recent["date"], recent["bb_upper"], recent["bb_lower"], alpha=0.1, color="#388bfd", label="BB Bands")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, fontsize=7)
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    # RSI chart
    st.markdown("**📊 RSI (Relative Strength Index)**")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot(recent["date"], recent["rsi"], color="#388bfd", linewidth=2)
    ax2.axhline(y=70, color="#f85149", linewidth=1.5, linestyle="--", label="Overbought (70)")
    ax2.axhline(y=30, color="#3fb950", linewidth=1.5, linestyle="--", label="Oversold (30)")
    ax2.fill_between(recent["date"], recent["rsi"], 70, where=(recent["rsi"] >= 70), color="#f85149", alpha=0.3)
    ax2.fill_between(recent["date"], recent["rsi"], 30, where=(recent["rsi"] <= 30), color="#3fb950", alpha=0.3)
    ax2.set_ylim(0, 100)
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    plt.xticks(rotation=45, fontsize=7)
    plt.tight_layout()
    st.pyplot(fig2)

col3, col4 = st.columns(2)

with col3:
    # MACD chart
    st.markdown("**📉 MACD**")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.plot(recent["date"], recent["macd"],        color="#388bfd", linewidth=2,   label="MACD")
    ax3.plot(recent["date"], recent["macd_signal"], color="#e3b341", linewidth=1.5, label="Signal")
    ax3.bar(recent["date"],  recent["macd_diff"],
            color=["#3fb950" if x > 0 else "#f85149" for x in recent["macd_diff"]],
            alpha=0.5, label="Histogram")
    ax3.axhline(y=0, color="#e6edf3", linewidth=0.8, linestyle="--")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    plt.xticks(rotation=45, fontsize=7)
    plt.tight_layout()
    st.pyplot(fig3)

with col4:
    # Sentiment breakdown
    st.markdown("**🧠 News Sentiment Breakdown**")
    sentiment_counts = coin_sentiment["sentiment_label"].value_counts()
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    colors_map = {"Positive": "#3fb950", "Neutral": "#e3b341", "Negative": "#f85149"}
    bars = ax4.bar(
        sentiment_counts.index,
        sentiment_counts.values,
        color=[colors_map.get(x, "#388bfd") for x in sentiment_counts.index]
    )
    for bar, val in zip(bars, sentiment_counts.values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                str(val), ha="center", color="#e6edf3", fontsize=10)
    ax4.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    st.pyplot(fig4)

st.divider()

# ─── SECTION 3: News & Alerts ─────────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("📰 Latest News & Sentiment")
    coin_news = coin_sentiment[["headline", "sentiment_score", "sentiment_label", "published_at"]].head(10)
    for _, row in coin_news.iterrows():
        color = "#3fb950" if row["sentiment_label"] == "Positive" else "#f85149" if row["sentiment_label"] == "Negative" else "#e3b341"
        st.markdown(f"""
        <div class="card">
            <small style="color:{color}">● {row['sentiment_label']} ({row['sentiment_score']:.3f})</small><br>
            <span style="font-size:0.9em">{row['headline']}</span><br>
            <small style="color:#8b949e">{row['published_at']}</small>
        </div>
        """, unsafe_allow_html=True)

with col6:
    st.subheader("🚨 Live Alert Log")
    st.markdown("""
    <div class="card">
        <p style="color:#8b949e">Alerts are sent to your Telegram in real time.</p>
        <p style="color:#8b949e">Run <code>event_detector.py</code> to start monitoring.</p>
    </div>
    """, unsafe_allow_html=True)

    # Show keyword alerts from latest news
    all_news = coin_sentiment[["coin_id", "headline", "sentiment_score", "sentiment_label"]].copy()
    critical_kw = ["hack","exploit","ban","illegal","shutdown","fraud","stolen","breach"]
    major_kw    = ["regulation","sec","lawsuit","government","federal","trump","elon"]
    bullish_kw  = ["etf","adoption","rally","surge","all time high","bullish","upgrade"]

    for _, row in all_news.iterrows():
        h = str(row["headline"]).lower()
        if any(kw in h for kw in critical_kw):
            st.markdown(f'<div class="alert-critical">🚨 <b>CRITICAL</b> — {row["headline"]}</div>', unsafe_allow_html=True)
        elif any(kw in h for kw in major_kw):
            st.markdown(f'<div class="alert-major">⚠️ <b>MAJOR</b> — {row["headline"]}</div>', unsafe_allow_html=True)
        elif any(kw in h for kw in bullish_kw):
            st.markdown(f'<div class="alert-bullish">🚀 <b>BULLISH</b> — {row["headline"]}</div>', unsafe_allow_html=True)

st.divider()

# ─── SECTION 4: Market Overview ───────────────────────────────────────────────
st.subheader("🌍 Full Market Overview")
col7, col8 = st.columns(2)

with col7:
    st.markdown("**💰 Current Prices**")
    fig5, ax5 = plt.subplots(figsize=(8, 4))
    df_no_btc = predictions[predictions["coin_id"] != "bitcoin"]
    bars = ax5.bar(df_no_btc["coin_id"], df_no_btc["current_price"], color="#388bfd")
    for bar, val in zip(bars, df_no_btc["current_price"]):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"${val:,.0f}", ha="center", color="#e6edf3", fontsize=9)
    ax5.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    st.pyplot(fig5)

with col8:
    st.markdown("**📊 Predicted Change % Tomorrow**")
    fig6, ax6 = plt.subplots(figsize=(8, 4))
    colors6 = ["#3fb950" if x > 0 else "#f85149" for x in predictions["change_pct"]]
    bars6 = ax6.bar(predictions["coin_id"], predictions["change_pct"], color=colors6)
    ax6.axhline(y=0, color="#e6edf3", linewidth=0.8, linestyle="--")
    for bar, val in zip(bars6, predictions["change_pct"]):
        ax6.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + (0.01 if val > 0 else -0.03),
                f"{val:+.2f}%", ha="center", color="#e6edf3", fontsize=9)
    ax6.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    st.pyplot(fig6)

# Footer
st.markdown("""
<div style="text-align:center; color:#8b949e; margin-top:30px; padding:20px;
            border-top: 1px solid #30363d;">
    🤖 Powered by CoinGecko API + NewsAPI + Random Forest ML<br>
    📊 Technical Indicators: RSI, MACD, Bollinger Bands<br>
    🚨 Real-time Telegram Alerts Active
</div>
""", unsafe_allow_html=True)