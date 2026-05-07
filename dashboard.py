import html
import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import ta
from dotenv import load_dotenv
from sqlalchemy import create_engine

from model import build_model


load_dotenv()
DB_URL = os.getenv("DB_URL")

st.set_page_config(
    page_title="CryptoAI Dashboard",
    page_icon=":material/monitoring:",
    layout="wide",
)

if not DB_URL:
    st.error("DB_URL is missing. Add it to your .env file, then restart Streamlit.")
    st.stop()

engine = create_engine(DB_URL, pool_pre_ping=True)

GREEN = "#3fb950"
RED = "#f85149"
YELLOW = "#e3b341"
BLUE = "#388bfd"
TEXT = "#e6edf3"
MUTED = "#8b949e"
PANEL = "#161b22"
BORDER = "#30363d"


st.markdown(
    f"""
<style>
    .stApp {{ background-color: #0d1117; color: {TEXT}; }}
    div[data-testid="metric-container"] {{
        background-color: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 14px;
    }}
    div[data-testid="stMetricValue"] {{ color: {TEXT}; }}
    .stSelectbox label, h1, h2, h3, h4 {{ color: {TEXT}; }}
    .hero {{
        background: linear-gradient(90deg, #1f6feb, #388bfd);
        padding: 24px;
        border-radius: 8px;
        margin-bottom: 20px;
    }}
    .hero h1 {{ color: white; margin: 0; font-size: 2.35rem; }}
    .hero p {{ color: #cdd9e5; margin: 6px 0 0 0; }}
    .card {{
        background-color: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 14px;
        margin: 6px 0;
    }}
    .card h4, .card h2, .card p {{ margin-top: 0; }}
    .muted {{ color: {MUTED}; }}
    .alert-critical, .alert-major, .alert-bullish {{
        padding: 10px 12px;
        border-radius: 6px;
        margin: 6px 0;
    }}
    .alert-critical {{ background-color: #3d1a1a; border-left: 4px solid {RED}; }}
    .alert-major {{ background-color: #2d2a1a; border-left: 4px solid {YELLOW}; }}
    .alert-bullish {{ background-color: #1a2d1a; border-left: 4px solid {GREEN}; }}
</style>
""",
    unsafe_allow_html=True,
)

plt.rcParams.update(
    {
        "figure.facecolor": "#0d1117",
        "axes.facecolor": PANEL,
        "axes.edgecolor": BORDER,
        "axes.labelcolor": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "text.color": TEXT,
        "grid.color": BORDER,
        "legend.facecolor": PANEL,
        "legend.edgecolor": BORDER,
    }
)


def safe_text(value):
    return html.escape("" if pd.isna(value) else str(value))


def money(value, digits=2):
    if pd.isna(value):
        return "N/A"
    return f"${value:,.{digits}f}"


def render_chart(fig):
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)


@st.cache_data(ttl=300, show_spinner=False)
def load_all_data(force_retrain=False):
    if force_retrain:
        predictions_df = build_model()
    else:
        try:
            predictions_df = pd.read_sql("SELECT * FROM predictions", engine)
        except Exception:
            predictions_df = pd.DataFrame()

        if predictions_df.empty:
            predictions_df = build_model()

    prices_df = pd.read_sql("SELECT * FROM historical_prices", engine)
    sentiment_df = pd.read_sql("SELECT * FROM news_sentiment", engine)

    if not prices_df.empty and "date" in prices_df:
        prices_df["date"] = pd.to_datetime(prices_df["date"], errors="coerce")
    if not sentiment_df.empty and "published_at" in sentiment_df:
        sentiment_df["published_at"] = pd.to_datetime(
            sentiment_df["published_at"], errors="coerce"
        )

    return predictions_df, prices_df, sentiment_df


def add_price_indicators(coin_prices):
    coin_prices = coin_prices.sort_values("date").copy()
    coin_prices["ma7"] = coin_prices["price"].rolling(7).mean()
    coin_prices["ma30"] = coin_prices["price"].rolling(30).mean()
    coin_prices["rsi"] = ta.momentum.RSIIndicator(coin_prices["price"], window=14).rsi()

    macd_ind = ta.trend.MACD(coin_prices["price"])
    coin_prices["macd"] = macd_ind.macd()
    coin_prices["macd_signal"] = macd_ind.macd_signal()
    coin_prices["macd_diff"] = macd_ind.macd_diff()

    bb = ta.volatility.BollingerBands(coin_prices["price"], window=20)
    coin_prices["bb_upper"] = bb.bollinger_hband()
    coin_prices["bb_lower"] = bb.bollinger_lband()

    return coin_prices.dropna()


def prediction_card(row):
    change = row["change_pct"]
    color = GREEN if change > 0 else RED
    direction = "Up" if change > 0 else "Down"
    sentiment_label = (
        "Positive"
        if row["sentiment_score"] > 0.2
        else "Negative"
        if row["sentiment_score"] < -0.2
        else "Neutral"
    )
    rsi_label = (
        "Overbought" if row["rsi"] > 70 else "Oversold" if row["rsi"] < 30 else "Neutral"
    )

    st.markdown(
        f"""
    <div class="card">
        <h4>{direction}: {safe_text(row["coin_id"]).upper()}</h4>
        <h2 style="color:{color}">{money(row["predicted_price"])}</h2>
        <p style="color:{color}">{change:+.2f}%</p>
        <hr style="border-color:{BORDER}">
        <small>Current: {money(row["current_price"])}</small><br>
        <small>RSI: {row["rsi"]:.1f} ({rsi_label})</small><br>
        <small>Sentiment: {sentiment_label}</small><br>
        <small>MAE: {money(row["mae"])}</small><br>
        <small>Top Signal: {safe_text(row["top_feature"])}</small>
    </div>
    """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
<div class="hero">
    <h1>CryptoAI Prediction Dashboard</h1>
    <p>Machine learning predictions, technical indicators, news sentiment, and alerts</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Controls")
    force_retrain = st.button("Retrain model", type="primary")
    if st.button("Clear dashboard cache"):
        st.cache_data.clear()
        st.rerun()

try:
    loading_message = (
        "Retraining AI model and loading market data..."
        if force_retrain
        else "Loading saved predictions and market data..."
    )
    with st.spinner(loading_message):
        predictions, prices, sentiment = load_all_data(force_retrain)
except Exception as exc:
    st.error("Dashboard data could not be loaded.")
    st.exception(exc)
    st.stop()

if predictions.empty:
    st.warning("No predictions were generated. Check your historical price data.")
    st.stop()

if "prediction_date" in predictions.columns and predictions["prediction_date"].notna().any():
    latest_prediction_date = predictions["prediction_date"].dropna().max()
    st.caption(f"Showing saved predictions from {latest_prediction_date}. Use Retrain model in the sidebar to refresh them.")
else:
    st.caption("Showing saved predictions. Use Retrain model in the sidebar to refresh them.")

required_prediction_cols = {
    "coin_id",
    "current_price",
    "predicted_price",
    "change_pct",
    "sentiment_score",
    "rsi",
    "top_feature",
    "mae",
}
missing = required_prediction_cols - set(predictions.columns)
if missing:
    st.error(f"Predictions are missing required columns: {', '.join(sorted(missing))}")
    st.stop()

st.subheader("Tomorrow's AI Price Predictions")
card_cols = st.columns(min(5, len(predictions)))
for i, (_, row) in enumerate(predictions.iterrows()):
    with card_cols[i % len(card_cols)]:
        prediction_card(row)

st.divider()

st.subheader("Deep Coin Analysis")
coin = st.selectbox("Select Coin", predictions["coin_id"].dropna().tolist())
coin_prices = prices[prices["coin_id"] == coin].copy()
coin_sentiment = sentiment[sentiment["coin_id"] == coin].copy()

if coin_prices.empty or len(coin_prices) < 35:
    st.warning("Not enough price history is available for this coin yet.")
    st.stop()

coin_prices = add_price_indicators(coin_prices)
recent = coin_prices.tail(90)

if recent.empty:
    st.warning("Not enough clean indicator data is available for this coin yet.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Price History + Moving Averages + Bollinger Bands**")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(recent["date"], recent["price"], color=BLUE, linewidth=2, label="Price")
    ax.plot(recent["date"], recent["ma7"], color=GREEN, linewidth=1.5, label="MA7", linestyle="--")
    ax.plot(recent["date"], recent["ma30"], color=YELLOW, linewidth=1.5, label="MA30", linestyle="--")
    ax.fill_between(recent["date"], recent["bb_upper"], recent["bb_lower"], alpha=0.12, color=BLUE, label="BB Bands")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    render_chart(fig)

with col2:
    st.markdown("**RSI (Relative Strength Index)**")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot(recent["date"], recent["rsi"], color=BLUE, linewidth=2)
    ax2.axhline(y=70, color=RED, linewidth=1.5, linestyle="--", label="Overbought (70)")
    ax2.axhline(y=30, color=GREEN, linewidth=1.5, linestyle="--", label="Oversold (30)")
    ax2.fill_between(recent["date"], recent["rsi"], 70, where=(recent["rsi"] >= 70), color=RED, alpha=0.3)
    ax2.fill_between(recent["date"], recent["rsi"], 30, where=(recent["rsi"] <= 30), color=GREEN, alpha=0.3)
    ax2.set_ylim(0, 100)
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    fig2.autofmt_xdate(rotation=45)
    fig2.tight_layout()
    render_chart(fig2)

col3, col4 = st.columns(2)

with col3:
    st.markdown("**MACD**")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.plot(recent["date"], recent["macd"], color=BLUE, linewidth=2, label="MACD")
    ax3.plot(recent["date"], recent["macd_signal"], color=YELLOW, linewidth=1.5, label="Signal")
    ax3.bar(
        recent["date"],
        recent["macd_diff"],
        color=[GREEN if x > 0 else RED for x in recent["macd_diff"]],
        alpha=0.5,
        label="Histogram",
    )
    ax3.axhline(y=0, color=TEXT, linewidth=0.8, linestyle="--")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    fig3.autofmt_xdate(rotation=45)
    fig3.tight_layout()
    render_chart(fig3)

with col4:
    st.markdown("**News Sentiment Breakdown**")
    sentiment_counts = coin_sentiment["sentiment_label"].value_counts() if not coin_sentiment.empty else pd.Series(dtype=int)
    if sentiment_counts.empty:
        st.info("No news sentiment rows found for this coin.")
    else:
        fig4, ax4 = plt.subplots(figsize=(8, 4))
        colors_map = {"Positive": GREEN, "Neutral": YELLOW, "Negative": RED}
        bars = ax4.bar(
            sentiment_counts.index,
            sentiment_counts.values,
            color=[colors_map.get(x, BLUE) for x in sentiment_counts.index],
        )
        for bar, val in zip(bars, sentiment_counts.values):
            ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, str(val), ha="center", color=TEXT, fontsize=10)
        ax4.grid(True, alpha=0.3, axis="y")
        fig4.tight_layout()
        render_chart(fig4)

st.divider()

col5, col6 = st.columns(2)

with col5:
    st.subheader("Latest News & Sentiment")
    if coin_sentiment.empty:
        st.info("No news articles found for this coin.")
    else:
        coin_news = coin_sentiment.sort_values("published_at", ascending=False).head(10)
        for _, row in coin_news.iterrows():
            label = row.get("sentiment_label", "Neutral")
            color = GREEN if label == "Positive" else RED if label == "Negative" else YELLOW
            score = row.get("sentiment_score", 0)
            st.markdown(
                f"""
        <div class="card">
            <small style="color:{color}">{safe_text(label)} ({score:.3f})</small><br>
            <span style="font-size:0.9em">{safe_text(row.get("headline", ""))}</span><br>
            <small class="muted">{safe_text(row.get("published_at", ""))}</small>
        </div>
        """,
                unsafe_allow_html=True,
            )

with col6:
    st.subheader("Live Alert Log")
    st.markdown(
        """
    <div class="card">
        <p class="muted">Alerts are sent to Telegram when the event detector is running.</p>
        <p class="muted">Start monitoring with <code>python event_detector.py</code>.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    critical_kw = ["hack", "exploit", "ban", "illegal", "shutdown", "fraud", "stolen", "breach"]
    major_kw = ["regulation", "sec", "lawsuit", "government", "federal", "trump", "elon"]
    bullish_kw = ["etf", "adoption", "rally", "surge", "all time high", "bullish", "upgrade"]

    alert_news = sentiment.copy()
    if "published_at" in alert_news:
        alert_news = alert_news.sort_values("published_at", ascending=False)

    shown_alerts = 0
    for _, row in alert_news.head(100).iterrows():
        coin_label = safe_text(row.get("coin_id", "")).upper()
        headline = safe_text(row.get("headline", ""))
        headline_lower = headline.lower()
        if any(kw in headline_lower for kw in critical_kw):
            st.markdown(f'<div class="alert-critical"><b>CRITICAL</b> - {coin_label}: {headline}</div>', unsafe_allow_html=True)
            shown_alerts += 1
        elif any(kw in headline_lower for kw in major_kw):
            st.markdown(f'<div class="alert-major"><b>MAJOR</b> - {coin_label}: {headline}</div>', unsafe_allow_html=True)
            shown_alerts += 1
        elif any(kw in headline_lower for kw in bullish_kw):
            st.markdown(f'<div class="alert-bullish"><b>BULLISH</b> - {coin_label}: {headline}</div>', unsafe_allow_html=True)
            shown_alerts += 1
    if shown_alerts == 0:
        st.info("No keyword alerts found in the latest market news.")

st.divider()

st.subheader("Full Market Overview")
col7, col8 = st.columns(2)

with col7:
    st.markdown("**Current Prices**")
    fig5, ax5 = plt.subplots(figsize=(8, 4))
    market_df = predictions[predictions["coin_id"] != "bitcoin"].copy()
    if market_df.empty:
        market_df = predictions.copy()
    bars = ax5.bar(market_df["coin_id"], market_df["current_price"], color=BLUE)
    for bar, val in zip(bars, market_df["current_price"]):
        ax5.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"${val:,.0f}", ha="center", va="bottom", color=TEXT, fontsize=9)
    ax5.grid(True, alpha=0.3, axis="y")
    fig5.tight_layout()
    render_chart(fig5)

with col8:
    st.markdown("**Predicted Change % Tomorrow**")
    fig6, ax6 = plt.subplots(figsize=(8, 4))
    colors6 = [GREEN if x > 0 else RED for x in predictions["change_pct"]]
    bars6 = ax6.bar(predictions["coin_id"], predictions["change_pct"], color=colors6)
    ax6.axhline(y=0, color=TEXT, linewidth=0.8, linestyle="--")
    for bar, val in zip(bars6, predictions["change_pct"]):
        offset = 0.02 if val >= 0 else -0.05
        ax6.text(bar.get_x() + bar.get_width() / 2, val + offset, f"{val:+.2f}%", ha="center", color=TEXT, fontsize=9)
    ax6.grid(True, alpha=0.3, axis="y")
    fig6.tight_layout()
    render_chart(fig6)

st.markdown(
    """
<div style="text-align:center; color:#8b949e; margin-top:30px; padding:20px; border-top: 1px solid #30363d;">
    Powered by CoinGecko API + NewsAPI + machine learning<br>
    Technical indicators: RSI, MACD, Bollinger Bands<br>
    Real-time Telegram alerts available through event_detector.py
</div>
""",
    unsafe_allow_html=True,
)
