import yfinance as yf
import json

def check_fundamentals(symbol):
    print(f"Fetching fundamentals for {symbol}...")
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    # Filter for key fundamental metrics
    keys_of_interest = [
        'trailingPE', 'forwardPE', 'priceToBook', 'returnOnEquity', 
        'debtToEquity', 'profitMargins', 'revenueGrowth', 'operatingMargins',
        'freeCashflow', 'marketCap', 'longName', 'sector'
    ]
    
    filtered_info = {k: info.get(k) for k in keys_of_interest}
    print(json.dumps(filtered_info, indent=2))

if __name__ == "__main__":
    check_fundamentals("RELIANCE.NS")
