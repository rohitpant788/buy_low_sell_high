import sqlite3
import streamlit as st
import pandas as pd

def harvest_all():
    # Connect to the SQLite database or create it if it doesn't exist
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Create tables
    create_watchlist_tables(cursor)

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

def create_watchlist_tables(cursor):
    # Create a table to store watchlist names
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    ''')

    # Create a table to store watchlist data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watchlist_id INTEGER,
            stock_symbol TEXT,
            stock_price REAL,
            per_change REAL,
            dma_200_close REAL,
            percent_away_from_dma_200 REAL,
            dma_50_close REAL,
            price_50dma_200dma REAL,
            rsi REAL,
            rsi_rank INTEGER,
            dma_200_rank INTEGER,
            FOREIGN KEY (watchlist_id) REFERENCES watchlist_names (id)
        )
    ''')


def get_watchlists(cursor):
    try:
        cursor.execute("SELECT name FROM watchlist_names")
        watchlists = cursor.fetchall()
        return [row[0] for row in watchlists]
    except sqlite3.Error as e:
        print(f"Error retrieving watchlists: {e}")
        return []

# You can also create a function to insert watchlist names into the database
def insert_watchlist_name(cursor, watchlist_name):
    try:
        cursor.execute("INSERT INTO watchlist_names (name) VALUES (?)", (watchlist_name,))
        return True  # Return True on success
    except sqlite3.Error as e:
        print(f"Error inserting watchlist name: {e}")
        return False  # Return False on failure
    finally:
        cursor.connection.commit()  # Commit the transaction



def display_watchlist_data(cursor, selected_watchlist):
    cursor.execute('''
        SELECT
            wd.stock_symbol,
            wd.stock_price,
            wd.per_change,
            wd.dma_200_close,
            wd.percent_away_from_dma_200,
            wd.dma_50_close,
            wd.price_50dma_200dma,
            wd.rsi,
            wd.rsi_rank,
            wd.dma_200_rank
        FROM watchlist_data AS wd
        JOIN watchlist_names AS wn ON wd.watchlist_id = wn.id
        WHERE wn.name = ?
    ''', (selected_watchlist,))
    watchlist_data = cursor.fetchall()

    if not watchlist_data:
        st.warning("No data available for the selected watchlist.")
    else:
        # Convert the result to a DataFrame and add column names
        column_names = [description[0] for description in cursor.description]
        df = pd.DataFrame(watchlist_data, columns=column_names)

        # Define a dictionary to map original column names to custom names
        custom_column_names = {
            'stock_symbol': 'Symbol',
            'stock_price': 'Price',
            'per_change': '% Change',
            'dma_200_close': '200 DMA Close',
            'percent_away_from_dma_200': '% Away from 200 DMA',
            'dma_50_close': '50 DMA Close',
            'price_50dma_200dma': 'Price 50DMA/200DMA',
            'rsi': 'RSI',
            'rsi_rank': 'RSI Rank',
            'dma_200_rank': '200 DMA Rank'
        }

        # Rename the columns using the custom names
        df = df.rename(columns=custom_column_names)

        # Display the DataFrame as a table with custom headers
        st.write("Watchlist Data:")
        st.write(df, use_container_width=True)


def insert_stock_to_watchlist(cursor, watchlist_name, stock_symbol):
    try:
        # Check if the watchlist exists
        cursor.execute("SELECT id FROM watchlist_names WHERE name = ?", (watchlist_name,))
        watchlist_id = cursor.fetchone()

        if watchlist_id:
            # Watchlist exists, insert the stock into the watchlist_data table
            cursor.execute("""
                INSERT INTO watchlist_data (watchlist_id, stock_symbol)
                VALUES (?, ?)
            """, (watchlist_id[0], stock_symbol))

            # Commit the changes to the database
            cursor.connection.commit()

            return True
        else:
            # Watchlist does not exist
            return False
    except sqlite3.Error as e:
        # Handle database errors here
        print(f"Error inserting stock into watchlist: {e}")
        return False