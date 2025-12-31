import logging
import sqlite3
import os
from datetime import datetime
import pandas as pd
from multi_year_breakout import check_multi_year_breakout, fetch_and_store_stocks_data
from config import DATABASE_FILE_PATH

# Configure logging to see our debug prints
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_cache():
    symbol = "RELIANCE"
    print(f"--- Run 1: {symbol} ---")
    # This should fetch from web
    check_multi_year_breakout(symbol, years_gap=4)
    
    print("\n--- Verifying DB content ---")
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cache_info WHERE symbol=?", (symbol,))
    row = cursor.fetchone()
    print(f"Cache Entry: {row}")
    conn.close()

    print(f"\n--- Run 2: {symbol} ---")
    # This should hit cache
    check_multi_year_breakout(symbol, years_gap=4)

if __name__ == "__main__":
    # Clean up first
    if os.path.exists(DATABASE_FILE_PATH):
        try:
             # Just clear the entry
             conn = sqlite3.connect(DATABASE_FILE_PATH)
             conn.execute("DELETE FROM cache_info WHERE symbol='RELIANCE'")
             conn.execute("DELETE FROM historical_data WHERE symbol='RELIANCE'")
             conn.commit()
             conn.close()
        except:
            pass
            
    test_cache()
