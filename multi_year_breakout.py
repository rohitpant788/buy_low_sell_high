import datetime
import logging
# Constants
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import yfinance as yf

# Configure logging to print to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

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
    # Append '.NS' to the stock symbol for NSE
    stock_symbol = stock + '.NS'

    # Calculate start and end dates based on years_gap and weeks_back
    current_date = datetime.today()
    start_date = current_date - timedelta(days=365 * (years_gap + 10))
    end_date = current_date - timedelta(days=current_date.weekday() + 1 + (weeks_back * 7))  # Adjust for weeks back  # Exclude current week

    logger.info(f"Fetching data for {stock_symbol} from {start_date.date()} to {end_date.date()}")

    # Fetch historical data
    try:
        df = yf.download(stock_symbol, start=start_date, end=end_date)
        logger.info(f"Data fetched successfully for {stock_symbol}")
    except Exception as e:
        logger.error(f"Failed to download data for {stock_symbol}: {str(e)}")
        return False

    # Check if there is enough historical data
    if len(df) < 2:
        logger.warning(f"Not enough data available for {stock_symbol}")
        return False

    # Get the historical high within the specified range (excluding current week)
    historical_df = df[(df.index >= current_date - timedelta(days=365 * years_gap)) & (df.index < end_date)]
    historical_high = historical_df['High'].max()
    logger.info(f"The historical high for {stock_symbol} in the past {years_gap} years (excluding current week) is {historical_high}")

    # Get the maximum high price in the period before the years_gap
    previous_df = df[df.index < current_date - timedelta(days=365 * years_gap)]
    previous_high = previous_df['High'].max()
    logger.info(f"The previous high for {stock_symbol} before {years_gap} years is {previous_high}")

    # Apply buffer to the comparison of historical_high and previous_high
    historical_high_with_buffer = historical_high * (1 - buffer)
    logger.info(f"The historical high with buffer for {stock_symbol} is {historical_high_with_buffer}")

    # Get the current week's data, adjusted for weeks_back
    current_week_start = current_date - timedelta(days=current_date.weekday() + (weeks_back * 7))
    current_week_end = current_date  # Set the end date to today's date
    current_week_df = yf.download(stock_symbol, start=current_week_start, end=current_week_end)
    logger.info(f"Checking current week's data for {stock_symbol} from {current_week_start.date()} to {current_week_end.date()}")

    # Check if the latest price has just crossed the historical high with buffer
    if not current_week_df.empty:
        current_price = current_week_df['Close'].iloc[-1]
        logger.info(f"The current week's closing price for {stock_symbol} is {current_price}")

        # Apply buffer to the comparison
        current_price_with_buffer = current_price * (1 + buffer)
        logger.info(f"The current week's closing price for {stock_symbol} with buffer is {current_price_with_buffer}")

        if historical_high_with_buffer < previous_high and current_price_with_buffer > previous_high:
            logger.info(f"{stock_symbol} is giving a multi-year breakout!")
            return True

    logger.info(f"{stock_symbol} is not giving a multi-year breakout.")
    return False


def create_tradingview_link(symbol):
    tradingview_url = f"https://www.tradingview.com/chart/?symbol=NSE:{symbol}"
    return f'<a href="{tradingview_url}" target="_blank">{symbol}</a>'

def display_breakout_stocks(breakout_stocks, years_gap,buffer,weeks_back):
    st.subheader(f"Multi-Year Breakout Stocks ({years_gap} Years)")
    if breakout_stocks:
        # Initialize lists to store data
        stock_names = []
        historical_highs = []
        historical_highs_with_buffer = []
        previous_highs = []
        current_prices = []
        current_prices_with_buffer = []

        # Iterate over breakout stocks to fetch data
        for stock_symbol in breakout_stocks:
            stock_name = stock_symbol  # Assuming stock name is the same as symbol for this example
            stock_names.append(stock_name)

            # Fetch data for the stock
            stock_symbol_ns = stock_symbol + '.NS'  # Append .NS for NSE
            try:
                df = yf.download(stock_symbol_ns, period="1d")
                current_price = df['Close'].iloc[-1]

                # Fetch historical data for breakout analysis
                historical_high, historical_high_with_buffer, previous_high, current_price_with_buffer = get_stock_data(stock_symbol,years_gap,buffer,weeks_back)

                # Append data to respective lists
                historical_highs.append(historical_high)
                historical_highs_with_buffer.append(historical_high_with_buffer)
                previous_highs.append(previous_high)
                current_prices.append(current_price)
                current_prices_with_buffer.append(current_price_with_buffer)

            except Exception as e:
                logger.error(f"Error fetching data for {stock_symbol}: {str(e)}")

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

def get_stock_data(stock_symbol,years_gap=5,buffer=.05,weeks_back=0):
    # Append '.NS' to the stock symbol for NSE
    stock_symbol_ns = stock_symbol + '.NS'

    # Fetch historical data
    current_date = datetime.today()
    start_date = current_date - timedelta(days=365 * (years_gap + 10))
    end_date = current_date - timedelta(days=current_date.weekday() + 1 + (weeks_back * 7))

    try:
        df = yf.download(stock_symbol_ns, start=start_date, end=end_date)

        # Get historical high, previous high, current price
        historical_df = df[(df.index >= current_date - timedelta(days=365 * years_gap)) & (df.index < end_date)]
        historical_high = historical_df['High'].max()
        previous_df = df[df.index < current_date - timedelta(days=365 * years_gap)]
        previous_high = previous_df['High'].max()

        current_week_start = current_date - timedelta(days=current_date.weekday() + (weeks_back * 7))
        current_week_end = current_date
        current_week_df = yf.download(stock_symbol_ns, start=current_week_start, end=current_week_end)
        current_price = current_week_df['Close'].iloc[-1]

        # Apply buffer to the values
        historical_high_with_buffer = historical_high * (1 - buffer)
        current_price_with_buffer = current_price * (1 + buffer)

        return historical_high, historical_high_with_buffer, previous_high, current_price_with_buffer

    except Exception as e:
        logger.error(f"Error fetching data for {stock_symbol}: {str(e)}")
        return None, None, None, None