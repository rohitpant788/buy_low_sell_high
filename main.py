import datetime
import logging
import pickle
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import yfinance as yf

# Constants
from config import DATABASE_FILE_PATH
from logging_utils import get_log_messages
from watchlist_display import display_watchlist_data
from watchlist_management import get_watchlists, create_watchlist_tables, manage_watchlists
from datetime import datetime, timedelta

# Configure logging to print to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
# Create a Streamlit text area for logging
log_output = st.empty()

def main():
    st.title("Buy Low Sell High")

    # Display the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    st.write(f"Current Date and Time: {current_time}")


    # Create tabs for watchlist management and display
    tabs = st.sidebar.radio("Navigation", [ "Display Watchlist","Manage Watchlists","Upload CSV"])

    if tabs == "Manage Watchlists":

        # ---User Authnetication------
        names = ['Rohit Pant']
        usernames = ['rohit']

        # load hashed passwords
        file_path = Path(__file__).parent / "hashed_pw.pkl"
        with file_path.open("rb") as file:
            hashed_passwords = pickle.load(file)

        credentials = {"usernames": {}}

        for un, name, pw in zip(usernames, names, hashed_passwords):
            user_dict = {"name": name, "password": pw}
            credentials["usernames"].update({un: user_dict})

        authenticator = stauth.Authenticate(credentials, cookie_name="buy_low_sell_high", key="abcdef",
                                            cookie_expiry_days=30)

        name, authentication_status, username = authenticator.login("Login", "main")

        if authentication_status == False:
            st.error("UserName/ Password is incorrect")

        if authentication_status == None:
            st.error("Please enter your UserName and Password")

        if authentication_status:

            # Database initialization
            conn = sqlite3.connect(DATABASE_FILE_PATH)
            cursor = conn.cursor()

            # Harvest database tables
            create_watchlist_tables(cursor)

            # User interaction section for managing watchlists
            st.header("User Watchlist Management")

            # Display available watchlists as radio buttons and manage watchlists
            selected_watchlist = manage_watchlists(cursor, conn)

            # Close the database connection
            conn.close()

            authenticator.logout("Logout", "sidebar")

    elif tabs == "Display Watchlist":
        # Database initialization
        conn = sqlite3.connect(DATABASE_FILE_PATH)
        cursor = conn.cursor()

        # Harvest database tables
        create_watchlist_tables(cursor)

        # User interaction section for displaying watchlist data
        st.header("Display Watchlist Data")

        # Display available watchlists as radio buttons for display
        selected_watchlist = st.radio("Select a Watchlist", get_watchlists(cursor))



        # Display watchlist data in a table
        display_watchlist_data(cursor, selected_watchlist)

        # Display logs in a text area
        log_messages = get_log_messages()
        st.subheader("Log Messages")
        st.text_area("Log Messages", value=log_messages, height=200)

        # Close the database connection
        conn.close()

    elif tabs == "Upload CSV":
        st.header("Upload 52WeekHigh CSV")
        # Input fields for years_gap and buffer
        years_gap = st.slider("Years Gap", min_value=1, max_value=10, value=5, step=1,
                              help="Select the number of years for breakout analysis")
        buffer = st.slider("Buffer", min_value=0.01, max_value=0.10, value=0.05, step=0.01, format="%.2f",
                           help="Select the buffer percentage for breakout analysis")
        weeks_back = st.number_input("Weeks Back", min_value=0, value=0)
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            breakout_stocks = process_csv(uploaded_file, years_gap=years_gap, buffer=buffer,weeks_back=weeks_back)
            if breakout_stocks:
                st.success("Stocks giving a multi-year breakout:")
                for stock_symbol in breakout_stocks:
                    tradingview_url = f"https://www.tradingview.com/chart/?symbol=NSE:{stock_symbol}"
                    st.markdown(f"[{stock_symbol} Chart on TradingView]({tradingview_url})")
            else:
                st.info("No stocks are giving a multi-year breakout at the moment.")

        # Real-time logging display

        log_messages = get_log_messages()  # Fetch all log messages
        log_output.text_area("Log Messages", value=log_messages, height=200)


def process_csv(file, years_gap=5, buffer=0.05,weeks_back=0):
    # Read the CSV file
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    # Assuming the correct column name is 'Symbol'
    correct_column_name = 'Symbol'

    # Create a list to store results
    breakout_stocks = []

    # Iterate over the list of stocks
    for stock in df[correct_column_name]:
        logger.info(f"##########################################{stock}##################################")
        logger.info(f"Processing stock: {stock}")
        if check_multi_year_breakout(stock, years_gap=years_gap, buffer=buffer,weeks_back=weeks_back):
            breakout_stocks.append(stock)

    return breakout_stocks

# Function to check for multi-year breakout within the current week
def check_multi_year_breakout(stock, years_gap=5, buffer=0.05,weeks_back=0):
    # Append '.NS' to the stock symbol for NSE
    stock_symbol = stock + '.NS'

    # Calculate start and end dates based on years_gap and weeks_back
    current_date = datetime.today()
    start_date = current_date - timedelta(days=365 * (years_gap + 10))
    end_date = current_date - timedelta(
        days=current_date.weekday() + 1 + (weeks_back * 7))  # Adjust for weeks back  # Exclude current week

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

    # Get the current week's data
    current_week_start = current_date - timedelta(days=current_date.weekday())
    current_week_df = yf.download(stock_symbol, start=current_week_start, end=current_date)
    logger.info(f"Checking current week's data for {stock_symbol} from {current_week_start.date()} to {current_date.date()}")

    # Check if the latest price has just crossed the historical high with buffer
    if not current_week_df.empty:
        current_price = current_week_df['Close'].iloc[-1]
        current_week_high = current_week_df['High'].max()
        logger.info(f"The current week's high for {stock_symbol} is {current_week_high} and the closing price is {current_price}")

        # Apply buffer to the comparison
        current_week_high_with_buffer = current_week_high * (1 + buffer)
        logger.info(f"The current week's high for {stock_symbol} with buffer is {current_week_high_with_buffer}")

        if historical_high < previous_high and current_week_high_with_buffer > previous_high:
            logger.info(f"{stock_symbol} is giving a multi-year breakout!")
            return True

    logger.info(f"{stock_symbol} is not giving a multi-year breakout.")
    return False

if __name__ == "__main__":
    main()