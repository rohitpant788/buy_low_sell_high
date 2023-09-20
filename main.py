import datetime

import streamlit as st
import sqlite3

import pickle
from pathlib import Path

import streamlit_authenticator as stauth


# Constants
from config import DATABASE_FILE_PATH
from logging_utils import get_log_messages
from scheduler import reload_all_watchlists
from update_data import update_database
from watchlist_display import display_watchlist_data
from watchlist_management import get_watchlists, create_watchlist_tables, manage_watchlists

def main():
    st.title("Buy Low Sell High")

    # Display the current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    st.write(f"Current Date and Time: {current_time}")
    # Create tabs for watchlist management and display
    tabs = st.sidebar.radio("Navigation", [ "Display Watchlist","Manage Watchlists"])

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

if __name__ == "__main__":
    main()