import datetime
import logging
# Constants
import sqlite3
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import yfinance as yf

# Configure logging to print to console
from config import DATABASE_FILE_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def create_stocks_table():
    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = conn.cursor()

    # Create table to store historical data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date DATE,
            high REAL,
            low REAL,
            close REAL,
            adjusted_close REAL,
            volume INTEGER,
            UNIQUE(symbol, date)  -- Ensure unique entries for symbol and date
        )
    ''')

    # Create table to store cache information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            last_updated DATE,
            UNIQUE(symbol)  -- Ensure unique entries for symbol
        )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

def fetch_and_store_stocks_data(symbol, start_date, end_date):
    try:
        # Append '.NS' to the stock symbol for NSE
        stock_symbol = symbol + '.NS'
        # Fetch stock data from Yahoo Finance
        df = yf.download(stock_symbol, start=start_date, end=end_date)


        conn = sqlite3.connect(DATABASE_FILE_PATH)
        cursor = conn.cursor()

        # Insert data into historical_data table
        for index, row in df.iterrows():
            cursor.execute('''
                INSERT OR IGNORE INTO historical_data (symbol, date, high, low, close, adjusted_close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, index.date(), row['High'], row['Low'], row['Close'], row['Adj Close'], row['Volume']))

        # Update cache_info table
        cursor.execute('''
            INSERT OR REPLACE INTO cache_info (symbol, last_updated)
            VALUES (?, ?)
        ''', (symbol, datetime.today().date()))

        conn.commit()
        conn.close()

        logger.info(f"Data fetched and stored successfully for {symbol}")

    except Exception as e:
        logger.error(f"Error fetching or storing data for {symbol}: {str(e)}")


def process_csv(file, years_gap=5, buffer=0.05, weeks_back=0):
    # Read the CSV file
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    # Assuming the correct column name is 'Symbol'
    df.columns = df.columns.str.strip().str.lower()
    correct_column_name = 'symbol'

    # Create a list to store results
    breakout_stocks = []

    # Iterate over the list of stocks
    for stock in df[correct_column_name]:
        logger.info(f"##########################################{stock}##################################")
        logger.info(f"Processing stock: {stock}")
        if check_multi_year_breakout(stock, years_gap=years_gap, buffer=buffer, weeks_back=weeks_back):
            breakout_stocks.append(stock)

    return breakout_stocks

def process_manual_input(stock_symbols, years_gap=5, buffer=0.05, weeks_back=0):
    breakout_stocks = []

    # Iterate over the list of stocks
    for stock in stock_symbols:
        logger.info(f"##########################################{stock}##################################")
        logger.info(f"Processing stock: {stock}")
        if check_multi_year_breakout(stock, years_gap=years_gap, buffer=buffer, weeks_back=weeks_back):
            breakout_stocks.append(stock)

    return breakout_stocks

# Function to check for multi-year breakout within the current week
def check_multi_year_breakout(stock, years_gap=5, buffer=0.05, weeks_back=0):
    # Check cache for last updated date
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT last_updated FROM cache_info WHERE symbol = ?', (stock,))
    result = cursor.fetchone()

    if result:
        last_updated = datetime.strptime(result[0], '%Y-%m-%d').date()
        today = datetime.today().date()
        if (today - last_updated).days > 1:  # Update cache if more than 1 day old
            fetch_and_store_stocks_data(stock, last_updated, today)
    else:
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=20 * 365)
        fetch_and_store_stocks_data(stock, start_date, end_date)

    # Append '.NS' to the stock symbol for NSE
    stock_symbol = stock + '.NS'

    # Calculate start and end dates based on years_gap and weeks_back
    current_date = datetime.today()
    start_date = current_date - timedelta(days=365 * (years_gap + 10))
    end_date = current_date - timedelta(days=current_date.weekday() + 1 + (weeks_back * 7))  # Adjust for weeks back  # Exclude current week

    logger.info(f"Fetching data for {stock_symbol} from {start_date.date()} to {end_date.date()}")

    # Fetch historical data
    try:
        query = '''
            SELECT date, high, low, close, volume FROM historical_data
            WHERE symbol = ? AND date BETWEEN ? AND ?
        '''
        df = pd.read_sql_query(query, conn, params=(stock, start_date, end_date))
        df['date'] = pd.to_datetime(df['date'])  # Convert date column to datetime
        df.set_index('date', inplace=True)  # Set date as index
        logger.info(f"Data fetched successfully for {stock_symbol}")
    except Exception as e:
        logger.error(f"Failed to fetch data for {stock_symbol}: {str(e)}")
        conn.close()
        return False

    # Check if there is enough historical data
    if len(df) < 2:
        logger.warning(f"Not enough data available for {stock_symbol}")
        conn.close()
        return False

    # Get the historical high within the specified range (excluding current week)
    historical_df = df[(df.index >= current_date - timedelta(days=365 * years_gap)) & (df.index < end_date)]
    historical_high = historical_df['high'].max()
    logger.info(f"The historical high for {stock_symbol} in the past {years_gap} years (excluding current week) is {historical_high}")

    # Get the maximum high price in the period before the years_gap
    previous_df = df[df.index < current_date - timedelta(days=365 * years_gap)]
    previous_high = previous_df['high'].max()
    logger.info(f"The previous high for {stock_symbol} before {years_gap} years is {previous_high}")

    # Apply buffer to the comparison of historical_high and previous_high
    historical_high_with_buffer = historical_high * (1 - buffer)
    logger.info(f"The historical high with buffer for {stock_symbol} is {historical_high_with_buffer}")

    # Get the current week's data, adjusted for weeks_back
    current_week_start = current_date - timedelta(days=current_date.weekday() + (weeks_back * 7))
    current_week_end = current_date  # Set the end date to today's date

    try:
        current_week_query = '''
            SELECT date, high, low, close, volume FROM historical_data
            WHERE symbol = ? AND date BETWEEN ? AND ?
        '''
        current_week_df = pd.read_sql_query(current_week_query, conn, params=(stock, current_week_start, current_week_end))
        current_week_df['date'] = pd.to_datetime(current_week_df['date'])  # Convert date column to datetime
        current_week_df.set_index('date', inplace=True)  # Set date as index
        logger.info(f"Current week data fetched successfully for {stock_symbol}")
    except Exception as e:
        logger.error(f"Failed to fetch current week data for {stock_symbol}: {str(e)}")
        conn.close()
        return False

    # Check if the latest price has just crossed the historical high with buffer
    if not current_week_df.empty:
        current_price = current_week_df['close'].iloc[-1]
        logger.info(f"The current week's closing price for {stock_symbol} is {current_price}")

        # Apply buffer to the comparison
        current_price_with_buffer = current_price * (1 + buffer)
        logger.info(f"The current week's closing price for {stock_symbol} with buffer is {current_price_with_buffer}")

        if historical_high_with_buffer < previous_high and current_price_with_buffer > previous_high:
            logger.info(f"{stock_symbol} is giving a multi-year breakout!")
            conn.close()
            return True

    logger.info(f"{stock_symbol} is not giving a multi-year breakout.")
    conn.close()
    return False



def create_tradingview_link(symbol):
    tradingview_url = f"https://www.tradingview.com/chart/?symbol=NSE:{symbol}"
    return f'<a href="{tradingview_url}" target="_blank">{symbol}</a>'

def display_breakout_stocks(breakout_stocks, years_gap, buffer, weeks_back):
    st.subheader(f"Multi-Year Breakout Stocks ({years_gap} Years)")
    if breakout_stocks:
        # Initialize lists to store data
        stock_names = []
        historical_highs = []
        historical_highs_with_buffer = []
        previous_highs = []
        current_prices = []
        current_prices_with_buffer = []

        # Connect to the database
        conn = sqlite3.connect(DATABASE_FILE_PATH)

        # Iterate over breakout stocks to fetch data
        for stock_symbol in breakout_stocks:
            stock_name = stock_symbol  # Assuming stock name is the same as symbol for this example
            stock_names.append(stock_name)

            # Fetch historical data for breakout analysis
            historical_high, historical_high_with_buffer, previous_high, current_price_with_buffer = get_stock_data(stock_symbol, years_gap, buffer, weeks_back)

            # Fetch current price from the database
            current_date = datetime.today()
            current_week_start = current_date - timedelta(days=current_date.weekday() + (weeks_back * 7))
            current_week_end = current_date

            current_week_query = '''
                SELECT date, high, low, close, volume FROM historical_data
                WHERE symbol = ? AND date BETWEEN ? AND ?
            '''
            current_week_df = pd.read_sql_query(current_week_query, conn, params=(stock_symbol, current_week_start, current_week_end))
            current_week_df['date'] = pd.to_datetime(current_week_df['date'])  # Convert date column to datetime
            current_week_df.set_index('date', inplace=True)  # Set date as index

            if not current_week_df.empty:
                current_price = current_week_df['close'].iloc[-1]
            else:
                current_price = None

            # Append data to respective lists
            historical_highs.append(historical_high)
            historical_highs_with_buffer.append(historical_high_with_buffer)
            previous_highs.append(previous_high)
            current_prices.append(current_price)
            current_prices_with_buffer.append(current_price_with_buffer)

        # Close the database connection
        conn.close()

        # Create a DataFrame
        breakout_data = {
            'Stock Name': [create_tradingview_link(name) for name in stock_names],
            'Historical High': historical_highs,
            'Historical High With Buffer': historical_highs_with_buffer,
            'Previous High': previous_highs,
            'Current Price': current_prices,
            'Current Price with Buffer': current_prices_with_buffer
        }

        # Display as a table with HTML rendering enabled
        st.markdown(pd.DataFrame(breakout_data).to_html(escape=False), unsafe_allow_html=True)

    else:
        st.info("No stocks are giving a multi-year breakout at the moment.")


def get_stock_data(stock_symbol, years_gap=5, buffer=0.05, weeks_back=0):
    # Connect to the database
    conn = sqlite3.connect(DATABASE_FILE_PATH)

    try:
        # Calculate start and end dates based on years_gap and weeks_back
        current_date = datetime.today()
        start_date = current_date - timedelta(days=365 * (years_gap + 10))
        end_date = current_date - timedelta(days=current_date.weekday() + 1 + (weeks_back * 7))

        # Fetch historical data from the database
        query = '''
            SELECT date, high, low, close, volume FROM historical_data
            WHERE symbol = ? AND date BETWEEN ? AND ?
        '''
        df = pd.read_sql_query(query, conn, params=(stock_symbol, start_date, end_date))
        df['date'] = pd.to_datetime(df['date'])  # Convert date column to datetime
        df.set_index('date', inplace=True)  # Set date as index

        # Get historical high, previous high, current price
        historical_df = df[(df.index >= current_date - timedelta(days=365 * years_gap)) & (df.index < end_date)]
        historical_high = historical_df['high'].max()
        previous_df = df[df.index < current_date - timedelta(days=365 * years_gap)]
        previous_high = previous_df['high'].max()

        # Get the current week's data, adjusted for weeks_back
        current_week_start = current_date - timedelta(days=current_date.weekday() + (weeks_back * 7))
        current_week_end = current_date  # Set the end date to today's date

        current_week_query = '''
            SELECT date, high, low, close, volume FROM historical_data
            WHERE symbol = ? AND date BETWEEN ? AND ?
        '''
        current_week_df = pd.read_sql_query(current_week_query, conn, params=(stock_symbol, current_week_start, current_week_end))
        current_week_df['date'] = pd.to_datetime(current_week_df['date'])  # Convert date column to datetime
        current_week_df.set_index('date', inplace=True)  # Set date as index

        if not current_week_df.empty:
            current_price = current_week_df['close'].iloc[-1]
        else:
            current_price = None

        # Apply buffer to the values
        historical_high_with_buffer = historical_high * (1 - buffer)
        current_price_with_buffer = current_price * (1 + buffer) if current_price is not None else None

        return historical_high, historical_high_with_buffer, previous_high, current_price_with_buffer

    except Exception as e:
        logger.error(f"Error fetching data for {stock_symbol}: {str(e)}")
        return None, None, None, None

    finally:
        conn.close()
