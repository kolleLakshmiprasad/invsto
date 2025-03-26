from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import pandas as pd
from database import get_db
from models import Stock
from schemas import StockSchema

app = FastAPI()

# Function to fetch stock data from the database
def get_stock_data(db: Session):
    stocks = db.query(Stock).all()
    if not stocks:
        return None
    df = pd.DataFrame([{
        "date": stock.date,
        "close": float(stock.close)  # Convert Decimal to float
    } for stock in stocks])
    
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df

# Moving Average Crossover Strategy
def moving_average_strategy(db: Session, short_window=5, long_window=20):
    df = get_stock_data(db)
    if df is None or df.empty:
        return {"error": "No stock data available"}

    # Calculate moving averages
    df["short_ma"] = df["close"].rolling(window=short_window).mean()
    df["long_ma"] = df["close"].rolling(window=long_window).mean()

    # Generate buy/sell signals
    df["signal"] = 0  # Default to no signal
    df.loc[df["short_ma"] > df["long_ma"], "signal"] = 1  # Buy
    df.loc[df["short_ma"] < df["long_ma"], "signal"] = -1  # Sell

    # Calculate strategy performance (percentage return)
    df["returns"] = df["close"].pct_change()
    df["strategy_returns"] = df["returns"] * df["signal"].shift(1)

    total_return = df["strategy_returns"].sum()
    return {
        "total_return": round(total_return, 4),
        "buy_signals": int((df["signal"] == 1).sum()),
        "sell_signals": int((df["signal"] == -1).sum()),
    }

# API Endpoint to get strategy performance
@app.get("/strategy/performance")
def strategy_performance(db: Session = Depends(get_db)):
    return moving_average_strategy(db)
