import csv
import sqlite3

import streamlit as st


def create_watchlist_tables(cursor):
    # Create a table to store watchlist names
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- Add updated_at column
        )
    ''')

    # Create a table to store watchlist data with a UNIQUE constraint on stock_symbol
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_symbol TEXT UNIQUE,  -- Add UNIQUE constraint here
            stock_price REAL,
            per_change REAL,
            dma_200_close REAL,
            percent_away_from_dma_200 REAL,
            dma_50_close REAL,
            price_50dma_200dma REAL,
            rsi REAL,
            rsi_rank INTEGER,
            dma_200_rank INTEGER
        )
    ''')

    # Create a table to store the mapping between watchlists and stocks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist_stock_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watchlist_id INTEGER,
            stock_id INTEGER,
            FOREIGN KEY (watchlist_id) REFERENCES watchlist_names (id),
            FOREIGN KEY (stock_id) REFERENCES watchlist_data (id)
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

def insert_stocks_from_csv(cursor, watchlist_name, csv_content):
    try:
        # Check if the watchlist exists
        cursor.execute("SELECT id FROM watchlist_names WHERE name = ?", (watchlist_name,))
        watchlist_id = cursor.fetchone()

        if watchlist_id:
            # Watchlist exists, split CSV content by commas
            stocks = [stock.strip() for stock in csv_content.split(',')]
            stocks_added = 0
            stocks_failed = 0
            failed_stocks = []

            for stock_symbol in stocks:
                if stock_symbol:
                    # Check if the stock symbol already exists in watchlist_data
                    cursor.execute("""
                        SELECT id FROM watchlist_data
                        WHERE stock_symbol = ?
                    """, (stock_symbol,))
                    existing_stock = cursor.fetchone()

                    if existing_stock:
                        # The stock already exists, insert a new mapping
                        cursor.execute("""
                            INSERT INTO watchlist_stock_mapping (watchlist_id, stock_id)
                            VALUES (?, ?)
                        """, (watchlist_id[0], existing_stock[0]))
                    else:
                        # The stock does not exist, insert it into watchlist_data and create a new mapping
                        try:
                            # Insert the stock into the watchlist_data table
                            cursor.execute("""
                                INSERT INTO watchlist_data (stock_symbol)
                                VALUES (?)
                            """, (stock_symbol,))
                            stock_id = cursor.lastrowid  # Get the ID of the newly inserted stock

                            # Insert the mapping into the watchlist_stock_mapping table
                            cursor.execute("""
                                INSERT INTO watchlist_stock_mapping (watchlist_id, stock_id)
                                VALUES (?, ?)
                            """, (watchlist_id[0], stock_id))

                            stocks_added += 1
                        except sqlite3.Error as e:
                            # Handle individual stock insertion errors here
                            print(f"Error inserting stock '{stock_symbol}': {e}")
                            failed_stocks.append(stock_symbol)
                            stocks_failed += 1

            # Commit the changes to the database
            cursor.connection.commit()

            return stocks_added, stocks_failed, failed_stocks
        else:
            # Watchlist does not exist
            return 0, 0, []  # Return 0 to indicate that no stocks were added
    except sqlite3.Error as e:
        # Handle database errors here
        print(f"Error inserting stocks into watchlist: {e}")
        return 0, 0, []  # Return 0 to indicate that no stocks were added



def update_watchlist_name(cursor, old_name, new_name):
    try:
        cursor.execute("UPDATE watchlist_names SET name = ? WHERE name = ?", (new_name, old_name))
        return True  # Return True on success
    except sqlite3.Error as e:
        print(f"Error updating watchlist name: {e}")
        return False  # Return False on failure
    finally:
        cursor.connection.commit()  # Commit the transaction


def delete_stock_from_watchlist(cursor, selected_watchlist, stock_to_delete):
    try:
        # Get the watchlist_id for the selected watchlist
        cursor.execute("SELECT id FROM watchlist_names WHERE name = ?", (selected_watchlist,))
        watchlist_id = cursor.fetchone()

        if watchlist_id:
            # Find the stock_id from watchlist_stock_mapping
            cursor.execute("""
                SELECT stock_id FROM watchlist_stock_mapping
                WHERE watchlist_id = ? AND stock_id IN (
                    SELECT id FROM watchlist_data WHERE stock_symbol = ?
                )
            """, (watchlist_id[0], stock_to_delete))

            stock_id = cursor.fetchone()

            if stock_id:
                # Delete the stock from watchlist_stock_mapping
                cursor.execute("""
                    DELETE FROM watchlist_stock_mapping
                    WHERE watchlist_id = ? AND stock_id = ?
                """, (watchlist_id[0], stock_id[0]))

                # Commit the changes to the database
                cursor.connection.commit()

                return True
            else:
                return False  # Stock not found in the watchlist
        else:
            return False  # Watchlist not found
    except sqlite3.Error as e:
        # Handle database errors here
        print(f"Error deleting stock from watchlist: {e}")
        return False



def get_stocks_in_watchlist(cursor, watchlist_name):
    try:
        cursor.execute('''
            SELECT wd.stock_symbol
            FROM watchlist_stock_mapping AS wsm
            JOIN watchlist_names AS wn ON wsm.watchlist_id = wn.id
            JOIN watchlist_data AS wd ON wsm.stock_id = wd.id
            WHERE wn.name = ?
        ''', (watchlist_name,))
        stocks = cursor.fetchall()
        return [row[0] for row in stocks]
    except sqlite3.Error as e:
        print(f"Error retrieving stocks in watchlist: {e}")
        return []


def delete_watchlist(cursor, watchlist_name):
    try:
        cursor.execute("DELETE FROM watchlist_names WHERE name = ?", (watchlist_name,))
        cursor.execute("DELETE FROM watchlist_stock_mapping WHERE watchlist_id IN (SELECT id FROM watchlist_names WHERE name = ?)", (watchlist_name,))
        cursor.connection.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error deleting watchlist: {e}")
        return False


########################################################################################################################
def manage_watchlists(cursor):
    # User interaction section
    watchlist_name = st.text_input("Enter a new watchlist name:")

    if st.button("Create Watchlist"):
        if watchlist_name:
            if insert_watchlist_name(cursor, watchlist_name):
                st.success(f"Watchlist '{watchlist_name}' created successfully.")
                st.experimental_rerun()
            else:
                st.error("Failed to create the watchlist.")
        else:
            st.warning("Please enter a watchlist name.")

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
                selected_watchlist = new_watchlist_name
                #st.experimental_rerun()
            else:
                st.error("Failed to update the watchlist name.")
        else:
            st.warning("Please enter a new watchlist name.")

    # Add a section to add stocks to the selected watchlist
    st.subheader(f"Add Stocks to '{selected_watchlist}'")
    csv_content = st.text_area("Enter stock symbols (comma-separated):")

    if st.button("Add Stocks"):
        if csv_content:
            stocks_added, stocks_failed, failed_stocks = insert_stocks_from_csv(cursor, selected_watchlist, csv_content)

            if stocks_added > 0:
                st.success(f"Successfully added {stocks_added} stocks to '{selected_watchlist}'.")

            if stocks_failed > 0:
                st.error(f"Failed to add {stocks_failed} stocks to '{selected_watchlist}': {', '.join(failed_stocks)}")

            # st.experimental_rerun()
        else:
            st.warning("Please enter stock symbols in CSV format.")

    # Get stocks for the selected watchlist
    stocks_in_watchlist = get_stocks_in_watchlist(cursor, selected_watchlist)

    # Add a section to delete stocks from the selected watchlist
    st.subheader(f"Delete Stocks from '{selected_watchlist}'")
    stock_to_delete = st.selectbox("Select a Stock to Delete:", stocks_in_watchlist)
    if st.button("Delete Stock"):
        if stock_to_delete:
            if delete_stock_from_watchlist(cursor, selected_watchlist, stock_to_delete):
                st.success(f"Stock '{stock_to_delete}' deleted from '{selected_watchlist}'.")
                stocks_in_watchlist.remove(stock_to_delete)
                #st.experimental_rerun()
            else:
                st.error(f"Failed to delete stock '{stock_to_delete}' from '{selected_watchlist}'.")
        else:
            st.warning("Please select a stock to delete.")

    # Add a section to delete the entire watchlist
    st.subheader(f"Delete Watchlist '{selected_watchlist}'")
    if st.button("Delete Watchlist"):
        if delete_watchlist(cursor, selected_watchlist):
            st.success(f"Watchlist '{selected_watchlist}' deleted successfully.")
            watchlists.remove(selected_watchlist)
            # Clear the selected_watchlist as it no longer exists
            selected_watchlist = None
            #st.experimental_rerun()
        else:
            st.error(f"Failed to delete watchlist '{selected_watchlist}'.")

    # Return the selected watchlist name
    return selected_watchlist


