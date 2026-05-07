import pandas as pd
from textblob import TextBlob
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from extract_news import extract_news

load_dotenv()
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    if not text:
        return 0.0
    score = analyzer.polarity_scores(str(text))["compound"]
    return round(score, 4)

def get_sentiment_label(score):
    if score > 0.2:
        return "Positive"
    elif score < -0.2:
        return "Negative"
    else:
        return "Neutral"

def process_sentiment():
    df = extract_news()
    
    df["sentiment_score"] = df["headline"].apply(analyze_sentiment)
    df["sentiment_label"] = df["sentiment_score"].apply(get_sentiment_label)
    
    # Load into database
    df.to_sql("news_sentiment", engine, if_exists="replace", index=False)
    print(f"✅ Sentiment analyzed and loaded for {len(df)} articles!")
    print(df[["coin_id", "headline", "sentiment_score", "sentiment_label"]].head(10))
    return df

if __name__ == "__main__":
    process_sentiment()