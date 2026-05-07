import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from extract_prices import extract_historical_prices

load_dotenv()
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)

def load_prices():
    df = extract_historical_prices()
    df.to_sql("historical_prices", engine, if_exists="replace", index=False)
    print(f"✅ Loaded {len(df)} rows into historical_prices table!")

if __name__ == "__main__":
    load_prices()