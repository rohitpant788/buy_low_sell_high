import sqlite3

import streamlit as st


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

def update_watchlist_name(cursor, old_name, new_name):
    try:
        cursor.execute("UPDATE watchlist_names SET name = ? WHERE name = ?", (new_name, old_name))
        return True  # Return True on success
    except sqlite3.Error as e:
        print(f"Error updating watchlist name: {e}")
        return False  # Return False on failure
    finally:
        cursor.connection.commit()  # Commit the transaction

def manage_watchlists(cursor):
    # User interaction section
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