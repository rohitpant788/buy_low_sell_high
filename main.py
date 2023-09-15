import logging
import sqlite3

import streamlit as st

from config import DATABASE_FILE_PATH  # Specify the path to your SQLite database file
# Configure logging
from logging_utils import get_log_messages
from update_data import update_database
from watchlist_display import display_watchlist_data
from watchlist_management import manage_watchlists, create_watchlist_tables, get_watchlists

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to the SQLite database
conn = sqlite3.connect(DATABASE_FILE_PATH)


def main():
    st.title("Buy Low Sell High")
    # Create tabs for watchlist management and display
    tabs = st.sidebar.radio("Navigation", ["Manage Watchlists", "Display Watchlist"])

    # Database initialization
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = conn.cursor()

    # Harvest database tables
    create_watchlist_tables(cursor)

    if tabs == "Manage Watchlists":
        # User interaction section for managing watchlists
        st.header("User Watchlist Management")

        # Display available watchlists as radio buttons and manage watchlists
        selected_watchlist = manage_watchlists(cursor)

    elif tabs == "Display Watchlist":
        # User interaction section for displaying watchlist data
        st.header("Display Watchlist Data")

        # Display available watchlists as radio buttons for display
        selected_watchlist = st.radio("Select a Watchlist", get_watchlists(cursor))

        # Reload Data button
        if st.button("Reload Data"):
            with st.spinner("Reloading data..."):
                update_database(conn, selected_watchlist)

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
