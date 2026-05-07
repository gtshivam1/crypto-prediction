import pandas as pd
import numpy as np
from sqlalchemy import create_engine
try:
    from xgboost import XGBRegressor
except ModuleNotFoundError:
    XGBRegressor = None
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import ta
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)

def build_model():
    prices_df = pd.read_sql("SELECT * FROM historical_prices", engine)
    sentiment_df = pd.read_sql("""
        SELECT coin_id, AVG(sentiment_score) as avg_sentiment
        FROM news_sentiment
        GROUP BY coin_id
    """, engine)

    results = []

    for coin in prices_df["coin_id"].unique():
        print(f"Training model for {coin}...")

        coin_df = prices_df[prices_df["coin_id"] == coin].sort_values("date").reset_index(drop=True)

        # Basic features
        coin_df["prev_price"]    = coin_df["price"].shift(1)
        coin_df["prev_price_2"]  = coin_df["price"].shift(2)
        coin_df["prev_price_3"]  = coin_df["price"].shift(3)
        coin_df["price_change"]  = coin_df["price"].pct_change()
        coin_df["ma7"]           = coin_df["price"].rolling(7).mean()
        coin_df["ma30"]          = coin_df["price"].rolling(30).mean()
        coin_df["ma7_ma30_diff"] = coin_df["ma7"] - coin_df["ma30"]
        coin_df["volatility"]    = coin_df["price"].rolling(7).std()
        coin_df["volume_change"] = coin_df["total_volume"].pct_change()

        # Technical indicators
        coin_df["rsi"] = ta.momentum.RSIIndicator(coin_df["price"], window=14).rsi()

        macd = ta.trend.MACD(coin_df["price"])
        coin_df["macd"]        = macd.macd()
        coin_df["macd_signal"] = macd.macd_signal()
        coin_df["macd_diff"]   = macd.macd_diff()

        bb = ta.volatility.BollingerBands(coin_df["price"], window=20)
        coin_df["bb_upper"] = bb.bollinger_hband()
        coin_df["bb_lower"] = bb.bollinger_lband()
        coin_df["bb_width"] = coin_df["bb_upper"] - coin_df["bb_lower"]

        coin_df["next_price"]    = coin_df["price"].shift(-1)
        coin_df = coin_df.dropna()

        if len(coin_df) < 10:
            print(f"Skipping {coin}: not enough clean rows to train.")
            continue

        # Sentiment
        sentiment = sentiment_df[sentiment_df["coin_id"] == coin]["avg_sentiment"].values
        sentiment_score = sentiment[0] if len(sentiment) > 0 else 0
        coin_df["sentiment"] = sentiment_score

        X = coin_df[[
            "prev_price", "prev_price_2", "prev_price_3",
            "price_change", "ma7", "ma30", "ma7_ma30_diff",
            "volatility", "volume_change",
            "rsi", "macd", "macd_signal", "macd_diff",
            "bb_upper", "bb_lower", "bb_width",
            "sentiment"
        ]]
        y = coin_df["next_price"]

        if len(X) < 20:
            X_train, X_test, y_train, y_test = X, X, y, y
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

        if XGBRegressor is not None:
            model = XGBRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
            )
        else:
            print("xgboost is not installed. Using RandomForestRegressor fallback.")
            model = RandomForestRegressor(
                n_estimators=200,
                random_state=42,
                n_jobs=-1,
            )
        
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)

        # Feature importance
        importance = pd.Series(model.feature_importances_, index=X.columns)
        top_feature = importance.idxmax()

        # Predict tomorrow
        last_row = coin_df.iloc[-1]
        tomorrow_input = pd.DataFrame([{
            "prev_price":    last_row["price"],
            "prev_price_2":  coin_df.iloc[-2]["price"],
            "prev_price_3":  coin_df.iloc[-3]["price"],
            "price_change":  last_row["price_change"],
            "ma7":           last_row["ma7"],
            "ma30":          last_row["ma30"],
            "ma7_ma30_diff": last_row["ma7_ma30_diff"],
            "volatility":    last_row["volatility"],
            "volume_change": last_row["volume_change"],
            "rsi":           last_row["rsi"],
            "macd":          last_row["macd"],
            "macd_signal":   last_row["macd_signal"],
            "macd_diff":     last_row["macd_diff"],
            "bb_upper":      last_row["bb_upper"],
            "bb_lower":      last_row["bb_lower"],
            "bb_width":      last_row["bb_width"],
            "sentiment":     sentiment_score
        }])

        tomorrow_price = model.predict(tomorrow_input)[0]
        change_pct = ((tomorrow_price - last_row["price"]) / last_row["price"]) * 100

        results.append({
            "coin_id":         coin,
            "current_price":   last_row["price"],
            "predicted_price": round(tomorrow_price, 2),
            "change_pct":      round(change_pct, 2),
            "sentiment_score": sentiment_score,
            "rsi":             round(last_row["rsi"], 2),
            "macd":            round(last_row["macd"], 2),
            "top_feature":     top_feature,
            "mae":             round(mae, 2)
        })

        print(f"✅ {coin} — Current: ${last_row['price']:,.2f} | Predicted: ${tomorrow_price:,.2f} | Change: {change_pct:.2f}% | RSI: {last_row['rsi']:.2f} | MAE: ${mae:,.2f}")

    results_df = pd.DataFrame(results)
    if results_df.empty:
        return results_df

    results_df["prediction_date"] = pd.Timestamp.today().date()
    results_df.to_sql("predictions", engine, if_exists="replace", index=False)
    print("✅ Predictions saved to database!")
    return results_df

if __name__ == "__main__":
    df = build_model()
    print("\n📊 Final Predictions:")
    print(df)
