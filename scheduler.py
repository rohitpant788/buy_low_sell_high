import atexit
import sqlite3
import streamlit as st

from apscheduler.schedulers.background import BackgroundScheduler

# Initialize the scheduler
from config import DATABASE_FILE_PATH
from update_data import update_database
from watchlist_management import get_watchlists

scheduler = BackgroundScheduler()


# Function to reload data for all watchlists
def reload_all_watchlists():
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = conn.cursor()

    # Iterate through all watchlists and reload data for each
    watchlists = get_watchlists(cursor)
    for watchlist_name in watchlists:
        with st.spinner(f"Reloading data for '{watchlist_name}'..."):
            update_database(conn, watchlist_name)
            print(f"Data for '{watchlist_name}' reloaded.")

    conn.close()


# Schedule the reload_all_watchlists function to run every hour
scheduler.add_job(reload_all_watchlists, 'interval', hours=1)
#scheduler.add_job(reload_all_watchlists, 'interval', minutes=1)

# Start the scheduler
scheduler.start()

# Shutdown the scheduler gracefully when the program exits
atexit.register(lambda: scheduler.shutdown())
