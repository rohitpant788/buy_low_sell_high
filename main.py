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
from multi_year_breakout import process_csv, display_breakout_stocks, create_tradingview_link, process_manual_input, \
    create_stocks_table
from watchlist_display import display_watchlist_data
from watchlist_management import get_watchlists, create_watchlist_tables, manage_watchlists
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Buy Low Sell High",
    layout="wide",  # This will set the layout to wide mode
    #initial_sidebar_state="collapsed"  # This will collapse the sidebar initially
)
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
        years_gap = st.slider("Years Gap", min_value=1, max_value=10, value=10, step=1,
                              help="Select the number of years for breakout analysis")
        buffer = st.slider("Buffer", min_value=0.01, max_value=0.20, value=0.10, step=0.01, format="%.2f",
                           help="Select the buffer percentage for breakout analysis")
        weeks_back = st.number_input("Weeks Back", min_value=0, value=12)

        # Provide an option to upload a CSV file or input manually
        input_option = st.radio("Input Option", ["Upload CSV", "Manual Input"])

        if input_option == "Upload CSV":
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file is not None:
                if st.button("Analyze CSV"):
                    create_stocks_table()
                    if analyze:
                        breakout_stocks = process_csv(uploaded_file, years_gap=years_gap, buffer=buffer, weeks_back=weeks_back)
                        display_breakout_stocks(breakout_stocks,years_gap,buffer,weeks_back)
                    else:
                        df = pd.read_csv(uploaded_file)
                        df.columns = df.columns.str.strip().str.lower()  # Normalize column names to lowercase
                        if 'symbol' not in df.columns:
                            raise ValueError("CSV file must contain a 'symbol' column")
                        df['symbol'] = df['symbol'].apply(create_tradingview_link)
                        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
        else:
            default_symbols = "20MICRONS,21STCENMGM,AHIMSA,AIMTRON,ALEMBICLTD,ALPEXSOLAR,ALUWIND,AMEYA,ARVINDFASN,ASAHISONG,ASAL,ASALCBR,ASHOKA,AVPINFRA,AXISBANK,AXISCETF,AXISHCETF,BAJAJCON,BALUFORGE,BANKBEES,BASF,BAYERCROP,BBNPPGOLD,BEPL,BHARATFORG,BIKAJI,BIOCON,BLUECHIP,BLUEJET,BPL,BYKE,CHAMBLFERT,CHAVDA,CHOICEIN,CMRSL,CROMPTON,CROWN,DBL,DEEPAKNTR,DHANUKA,DIXON,DONEAR,DREDGECORP,EBBETF0430,EFACTOR,ELIN,EMMIL,ENSER,ESCORTS,ESG,EXCELINDUS,EXICOM,FACT,FEDERALBNK,FOSECOIND,GALLANTT,GANECOS,GAYAHWS,GEECEE,GEPIL,GMRP&UI,GODFRYPHLP,GRANULES,GRAVITA,GRINFRA,GSEC5IETF,HERCULES,HESTERBIO,HOACFOODS,HONDAPOWER,HSCL,HUHTAMAKI,IBREALEST,IIFLSEC,INDHOTEL,INDIANHUME,INOXGREEN,JINDALSTEL,JISLDVREQS,JNKINDIA,JSWENERGY,JSWINFRA,JSWSTEEL,JTEKTINDIA,JUNIORBEES,K2INFRA,KALYANKJIL,KAYA,KCK,KDL,KICL,KODYTECH,KRISHANA,KRISHNADEF,KSCL,LEMERITE,LGBFORGE,LIQUIDADD,LIQUIDSBI,LLOYDSENGG,LTF,LTFOODS,MAKEINDIA,MAPMYINDIA,MAWANASUG,MAXHEALTH,MEDIASSIST,MHRIL,MICEL,MID150BEES,MIDQ50ADD,MOHITIND,MON100,MOSMALL250,MOTHERSON,NAM-INDIA,NAVA,NFL,NOCIL,NV20BEES,OMINFRAL,OWAIS,PANAMAPET,PASHUPATI,PDMJEPAPER,PENINLAND,PERSISTENT,PILANIINVS,PKTEA,PNC,POKARNA,POLYCAB,POLYMED,PRECWIRE,PREMEXPLN,PRIMESECU,PUNJABCHEM,RACE,RAYMOND,RCF,REDTAPE,REFRACTORY,RKDL,RKFORGE,ROTO,SAMPANN,SANDESH,SAREGAMA,SCILAL,SENCO,SETFNIFBK,SHAKTIPUMP,SHILPAMED,SHRADHA,SILKFLEX,SJLOGISTIC,SKYGOLD,SMALLCAP,SMSPHARMA,SOMICONVEY,SPECTRUM,STOVEKRAFT,STYRENIX,SUMIT,SUMMITSEC,SUNTECK,SUPREMEPWR,SURAJEST,SURANAT&P,SUZLON,SWARAJENG,TBI,TCIFINANCE,TCLCONS,TECHLABS,TECHM,TEXINFRA,TGL,THANGAMAYL,THOMASCOOK,TIMETECHNO,TITAGARH,TNIDETF,UDAICEMENT,USK,UTIBANKETF,V2RETAIL,VGUARD,VILAS,VIVIANA,VMART,VSSL,WHIRLPOOL,WINDMACHIN,ZENITHEXPO,ZENSARTECH,ZTECH"
            manual_input = st.text_area("Enter stock symbols separated by commas", default_symbols)
            if manual_input:
                if st.button("Analyze Manual Input"):
                    create_stocks_table()
                    stock_symbols = [symbol.strip() for symbol in manual_input.split(",")]
                    if analyze:
                        stock_symbols = [symbol.strip() for symbol in manual_input.split(",")]
                        breakout_stocks = process_manual_input(stock_symbols, years_gap=years_gap, buffer=buffer, weeks_back=weeks_back)
                        display_breakout_stocks(breakout_stocks,years_gap,buffer,weeks_back)
                    else:
                        symbols_with_links = [create_tradingview_link(symbol) for symbol in stock_symbols]
                        df = pd.DataFrame({'Symbols': symbols_with_links})
                        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
