import sqlite3
import pandas as pd
from config import DATABASE_FILE_PATH

def verify_data(symbol):
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = conn.cursor()
    
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM historical_data WHERE symbol=?", (symbol,))
    count = cursor.fetchone()[0]
    print(f"Row count for {symbol}: {count}")
    
    if count > 0:
        cursor.execute("SELECT date, close FROM historical_data WHERE symbol=? ORDER BY date DESC LIMIT 5", (symbol,))
        rows = cursor.fetchall()
        print("Latest 5 rows:")
        for r in rows:
            print(r)
    else:
        print("No data found.")
        
    conn.close()

if __name__ == "__main__":
    verify_data("20MICRONS")
