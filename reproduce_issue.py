import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

symbol = "20MICRONS.NS"
print(f"Attempting to fetch data for {symbol}...")

try:
    # Mimic the app's behavior
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="1mo")
    
    if history.empty:
        print(" History is empty.")
    else:
        print(" History fetched successfully.")
        print(history.tail())
        
    print(f"Timezone: {ticker.info.get('timeZoneFullName')}")

except Exception as e:
    print(f"Error: {e}")
