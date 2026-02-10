import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str):
    """
    Fetches historical stock data for the given ticker using yfinance.
    Returns a list of dictionaries with date, open, high, low, close.
    """
    try:
        # Fetch data for the last 1 year or so to populate the chart
        stock = yf.Ticker(ticker)
        # 1y is a good default for a chart
        hist = stock.history(period="1y") 
        
        # Reset index to get Date as a column
        hist.reset_index(inplace=True)
        
        # Select relevant columns and rename if necessary (though frontend expects specific format)
        # Looking at frontend StockChart.vue might verify format, but usually Date, Close is enough.
        # Let's return Date, Open, High, Low, Close, Volume for potential candlestick charts
        
        data = []
        for index, row in hist.iterrows():
            data.append({
                "date": row["Date"].strftime("%Y-%m-%d"),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"]
            })
            
        return data
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return []

def get_stock_info(ticker: str):
    """
    Fetches basic info for a ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        return stock.info
    except Exception as e:
        print(f"Error fetching stock info for {ticker}: {e}")
        return {}
