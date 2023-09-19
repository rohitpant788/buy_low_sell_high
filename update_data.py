import pandas as pd
import logging
import sqlite3
from logging_utils import update_log_messages
from datetime import datetime
import get_nse_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_database(db_conn,watchlist_name):
    try:
        cursor = db_conn.cursor()

        # Store the current UTC time as the "updated_at" timestamp
        updated_at = datetime.now()

        # Update the database with the current timestamp in the updated_at column
        cursor.execute('''
                    UPDATE watchlist_names
                    SET updated_at = ?
                    WHERE name = ?
                ''', (updated_at, watchlist_name))

        cursor.execute('''
            SELECT wd.*
            FROM watchlist_data AS wd
            JOIN watchlist_stock_mapping AS wsm ON wd.id = wsm.stock_id
            JOIN watchlist_names AS wn ON wsm.watchlist_id = wn.id
            WHERE wn.name = ?
        ''', (watchlist_name,))
        rows = cursor.fetchall()

        # Create a list to store RSI and Price % from 200 DMA data and their corresponding row numbers
        rsi_data = []
        dma_data = []

        # Assuming watchlist_data is a list of tuples
        watchlist_df = pd.DataFrame(rows,
                                    columns=['id','stock_symbol', 'stock_price', 'per_change',
                                             'dma_200_close', 'percent_away_from_dma_200', 'dma_50_close',
                                             'price_50dma_200dma', 'rsi', 'rsi_rank', 'dma_200_rank'])

        for index, row in watchlist_df.iterrows():
            sym = row[1]

            # Get historical data
            candles = get_nse_data.get_historical_data(sym)
            df = pd.DataFrame(candles)

            log_message = f'Processing symbol {sym}'
            logger.info(log_message)
            update_log_messages(log_message)

            if not df.empty:
                # Get the last row of the DataFrame
                last_row = df.iloc[-1]

                # Update the database with relevant data
                cursor.execute(
                    """
                    UPDATE watchlist_data
                    SET
                        stock_price = ?,
                        per_change = ?,
                        dma_200_close = ?,
                        percent_away_from_dma_200 = ?,
                        dma_50_close = ?,
                        price_50dma_200dma = ?,
                        rsi = ?
                    WHERE stock_symbol = ?
                    """,
                    (
                        last_row['Close'],
                        last_row['% change for that Day'],
                        last_row['200 DMA (close)'],
                        last_row['Price % from 200 DMA'],
                        last_row['50 DMA (close)'],
                        last_row['Price < 50DMA < 200DMA'],
                        last_row['RSI'],
                        sym,
                    ),
                )

                # Store RSI and Price % from 200 DMA values and row number in the lists
                rsi_data.append((last_row['RSI'], sym))
                dma_data.append((last_row['Price % from 200 DMA'], sym))

        # Rank the stocks based on RSI (ascending order)
        rsi_data.sort(key=lambda x: x[0])
        for rank, (rsi, symbol) in enumerate(rsi_data, start=1):
            cursor.execute(
                """
                UPDATE watchlist_data
                SET rsi_rank = ?
                WHERE stock_symbol = ?
                """,
                (rank, symbol),
            )

        # Rank the stocks based on Price % from 200 DMA (ascending order)
        dma_data.sort(key=lambda x: x[0])
        for rank, (dma, symbol) in enumerate(dma_data, start=1):
            cursor.execute(
                """
                UPDATE watchlist_data
                SET dma_200_rank = ?
                WHERE stock_symbol = ?
                """,
                (rank, symbol),
            )

        # Commit the changes to the database
        db_conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error updating database: {e}")
