import sqlite3
from config import DATABASE_FILE_PATH

def clean_cache(symbol):
    print(f"Connecting to database at {DATABASE_FILE_PATH}...")
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = conn.cursor()
    
    # Check if entry exists
    cursor.execute("SELECT * FROM cache_info WHERE symbol=?", (symbol,))
    entry = cursor.fetchone()
    if entry:
        print(f"Found cache entry for {symbol}: {entry}")
        # Delete it
        cursor.execute("DELETE FROM cache_info WHERE symbol=?", (symbol,))
        cursor.execute("DELETE FROM historical_data WHERE symbol=?", (symbol,))
        conn.commit()
        print(f"Successfully deleted cache and historical data for {symbol}.")
    else:
        print(f"No cache entry found for {symbol}.")
        
    conn.close()

if __name__ == "__main__":
    clean_cache("20MICRONS")
