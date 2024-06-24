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
    tabs = st.sidebar.radio("Navigation", ["Display Watchlist", "Manage Watchlists", "Multi Year Breakout Stocks"])

    if tabs == "Manage Watchlists":
        # ---User Authentication------
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
            st.error("Username/Password is incorrect")

        if authentication_status == None:
            st.error("Please enter your Username and Password")

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

    elif tabs == "Multi Year Breakout Stocks":
        st.header("Multi-Year Breakout Analysis")

        # Add toggle button
        analyze = st.checkbox("Perform Analysis")

        # Input fields for years_gap and buffer
        years_gap = st.slider("Years Gap", min_value=1, max_value=10, value=5, step=1,
                              help="Select the number of years for breakout analysis")
        buffer = st.slider("Buffer", min_value=0.01, max_value=0.10, value=0.05, step=0.01, format="%.2f",
                           help="Select the buffer percentage for breakout analysis")
        weeks_back = st.number_input("Weeks Back", min_value=0, value=0)

        # Provide an option to upload a CSV file or input manually
        input_option = st.radio("Input Option", ["Upload CSV", "Manual Input"])

        if input_option == "Upload CSV":
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file is not None:
                if st.button("Analyze CSV"):
                    if analyze:
                        breakout_stocks = process_csv(uploaded_file, years_gap=years_gap, buffer=buffer, weeks_back=weeks_back)
                        display_breakout_stocks(breakout_stocks,years_gap,buffer,weeks_back)
                    else:
                        df = pd.read_csv(uploaded_file)
                        df.columns = df.columns.str.strip()
                        df['Symbol'] = df['Symbol'].apply(create_tradingview_link)
                        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
        else:
            default_symbols = "20MICRONS,21STCENMGM,AHIMSA,AIMTRON,ALEMBICLTD,ALPEXSOLAR,ALUWIND,AMEYA,ARVINDFASN,ASAHISONG,ASAL,ASALCBR,ASHOKA,AVPINFRA,AXISBANK,AXISCETF,AXISHCETF,BAJAJCON,BALUFORGE,BANKBEES,BASF,BAYERCROP,BBNPPGOLD,BEPL,BHARATFORG,BIKAJI,BIOCON,BLUECHIP,BLUEJET,BPL,BYKE,CHAMBLFERT,CHAVDA,CHOICEIN,CMRSL,CROMPTON,CROWN,DBL,DEEPAKNTR,DHANUKA,DIXON,DONEAR,DREDGECORP,EBBETF0430,EFACTOR,ELIN,EMMIL,ENSER,ESCORTS,ESG,EXCELINDUS,EXICOM,FACT,FEDERALBNK,FOSECOIND,GALLANTT,GANECOS,GAYAHWS,GEECEE,GEPIL,GMRP&UI,GODFRYPHLP,GRANULES,GRAVITA,GRINFRA,GSEC5IETF,HERCULES,HESTERBIO,HOACFOODS,HONDAPOWER,HSCL,HUHTAMAKI,IBREALEST,IIFLSEC,INDHOTEL,INDIANHUME,INOXGREEN,JINDALSTEL,JISLDVREQS,JNKINDIA,JSWENERGY,JSWINFRA,JSWSTEEL,JTEKTINDIA,JUNIORBEES,K2INFRA,KALYANKJIL,KAYA,KCK,KDL,KICL,KODYTECH,KRISHANA,KRISHNADEF,KSCL,LEMERITE,LGBFORGE,LIQUIDADD,LIQUIDSBI,LLOYDSENGG,LTF,LTFOODS,MAKEINDIA,MAPMYINDIA,MAWANASUG,MAXHEALTH,MEDIASSIST,MHRIL,MICEL,MID150BEES,MIDQ50ADD,MOHITIND,MON100,MOSMALL250,MOTHERSON,NAM-INDIA,NAVA,NFL,NOCIL,NV20BEES,OMINFRAL,OWAIS,PANAMAPET,PASHUPATI,PDMJEPAPER,PENINLAND,PERSISTENT,PILANIINVS,PKTEA,PNC,POKARNA,POLYCAB,POLYMED,PRECWIRE,PREMEXPLN,PRIMESECU,PUNJABCHEM,RACE,RAYMOND,RCF,REDTAPE,REFRACTORY,RKDL,RKFORGE,ROTO,SAMPANN,SANDESH,SAREGAMA,SCILAL,SENCO,SETFNIFBK,SHAKTIPUMP,SHILPAMED,SHRADHA,SILKFLEX,SJLOGISTIC,SKYGOLD,SMALLCAP,SMSPHARMA,SOMICONVEY,SPECTRUM,STOVEKRAFT,STYRENIX,SUMIT,SUMMITSEC,SUNTECK,SUPREMEPWR,SURAJEST,SURANAT&P,SUZLON,SWARAJENG,TBI,TCIFINANCE,TCLCONS,TECHLABS,TECHM,TEXINFRA,TGL,THANGAMAYL,THOMASCOOK,TIMETECHNO,TITAGARH,TNIDETF,UDAICEMENT,USK,UTIBANKETF,V2RETAIL,VGUARD,VILAS,VIVIANA,VMART,VSSL,WHIRLPOOL,WINDMACHIN,ZENITHEXPO,ZENSARTECH,ZTECH"
            manual_input = st.text_area("Enter stock symbols separated by commas", default_symbols)
            if manual_input:
                if st.button("Analyze Manual Input"):
                    stock_symbols = [symbol.strip() for symbol in manual_input.split(",")]
                    if analyze:
                        stock_symbols = [symbol.strip() for symbol in manual_input.split(",")]
                        breakout_stocks = process_manual_input(stock_symbols, years_gap=years_gap, buffer=buffer, weeks_back=weeks_back)
                        display_breakout_stocks(breakout_stocks,years_gap,buffer,weeks_back)
                    else:
                        symbols_with_links = [create_tradingview_link(symbol) for symbol in stock_symbols]
                        df = pd.DataFrame({'Symbols': symbols_with_links})
                        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)

        # Real-time logging display
        log_messages = get_log_messages()  # Fetch all log messages
        log_output.text_area("Log Messages", value=log_messages, height=200)

def process_csv(file, years_gap=5, buffer=0.05, weeks_back=0):
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

# def display_breakout_stocks(breakout_stocks):
#     if breakout_stocks:
#         st.success("Stocks giving a multi-year breakout:")
#         for stock_symbol in breakout_stocks:
#             tradingview_url = f"https://www.tradingview.com/chart/?symbol=NSE:{stock_symbol}"
#             st.markdown(f"[{stock_symbol} Chart on TradingView]({tradingview_url})")
#     else:
#         st.info("No stocks are giving a multi-year breakout at the moment.")

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

if __name__ == "__main__":
    main()
