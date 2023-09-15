import logging
import sqlite3

import streamlit as st

from config import DATABASE_FILE_PATH  # Specify the path to your SQLite database file
# Configure logging
from helper import harvest_all, insert_watchlist_name, get_watchlists, display_watchlist_data, create_watchlist_tables, \
    insert_stock_to_watchlist, update_watchlist_name
from logging_utils import get_log_messages
from update_data import update_database

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


    


    # User interaction section
    st.header("User Watchlist Management")
    watchlist_name = st.text_input("Enter a new watchlist name:")

    if st.button("Create Watchlist"):
        if watchlist_name:
            if insert_watchlist_name(cursor, watchlist_name):
                st.success(f"Watchlist '{watchlist_name}' created successfully.")
            else:
                st.error("Failed to create the watchlist.")
        else:
            st.warning("Please enter a watchlist name.")  # Add this line to prompt the user to enter a name

    # Display available watchlists as radio buttons
    watchlists = get_watchlists(cursor)
    selected_watchlist = st.radio("Select a Watchlist", watchlists)

    # Debugging: Print the watchlist_name
    print(f"Watchlist Name: {watchlist_name}")

    # Add a section to edit the selected watchlist name
    new_watchlist_name = st.text_input("Edit Watchlist Name:", selected_watchlist)
    if st.button("Save"):
        if new_watchlist_name:
            if update_watchlist_name(cursor, selected_watchlist, new_watchlist_name):
                st.success(f"Watchlist name updated to '{new_watchlist_name}'.")
                selected_watchlist = new_watchlist_name  # Update the selected watchlist name
            else:
                st.error("Failed to update the watchlist name.")
        else:
            st.warning("Please enter a new watchlist name.")

    # Add a section to add stocks to the selected watchlist
    st.subheader(f"Add Stocks to '{selected_watchlist}'")
    stock_symbol = st.text_input("Enter a stock symbol:")
    if st.button("Add Stock"):
        if stock_symbol:
            # You can add validation and error handling here if needed
            if insert_stock_to_watchlist(cursor, selected_watchlist, stock_symbol):
                st.success(f"Stock '{stock_symbol}' added to '{selected_watchlist}'.")
            else:
                st.error(f"Failed to add stock '{stock_symbol}' to '{selected_watchlist}'.")
        else:
            st.warning("Please enter a stock symbol.")

    # Display watchlist data in a table
    display_watchlist_data(cursor, selected_watchlist)

    # Reload Data button
    if st.button("Reload Data"):
        with st.spinner("Reloading data..."):
            update_database(conn, selected_watchlist)  # Modify this function to update the database

    # Display logs in a text area
    log_messages = get_log_messages()
    st.subheader("Log Messages")
    st.text_area("Log Messages", value=log_messages, height=200)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
