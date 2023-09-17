import pandas as pd
import streamlit as st


def display_watchlist_data(cursor, selected_watchlist):
    cursor.execute('''
        SELECT
            wd.stock_symbol,
            wd.stock_price,
            wd.per_change,
            wd.dma_200_close,
            wd.percent_away_from_dma_200,
            wd.dma_50_close,
            wd.price_50dma_200dma,
            wd.rsi,
            wd.rsi_rank,
            wd.dma_200_rank,
            wn.updated_at  -- Include the updated_at column from watchlist_names
        FROM watchlist_data AS wd
        JOIN watchlist_stock_mapping AS wsm ON wd.id = wsm.stock_id
        JOIN watchlist_names AS wn ON wsm.watchlist_id = wn.id
        WHERE wn.name = ?
    ''', (selected_watchlist,))

    watchlist_data = cursor.fetchall()

    if not watchlist_data:
        st.warning("No data available for the selected watchlist.")
    else:
        # Convert the result to a DataFrame and add column names
        column_names = [description[0] for description in cursor.description]
        df = pd.DataFrame(watchlist_data, columns=column_names)

        # Define a dictionary to map original column names to custom names
        custom_column_names = {
            'stock_symbol': 'Symbol',
            'stock_price': 'Price',
            'per_change': '% Change',
            'dma_200_close': '200 DMA Close',
            'percent_away_from_dma_200': '% Away from 200 DMA',
            'dma_50_close': '50 DMA Close',
            'price_50dma_200dma': 'Price < 50DMA <200DMA',
            'rsi': 'RSI',
            'rsi_rank': 'RSI Rank',
            'dma_200_rank': '200 DMA Rank',
            'updated_at': 'Updated At'  # Rename the updated_at column
        }

        # Rename the columns using the custom names
        df = df.rename(columns=custom_column_names)

        # Display the "Watchlist Data" message with the updated timestamp
        st.write(f"Watchlist Data: Updated At {df['Updated At'].iloc[0]} (Asia/Kolkata)")

        # Display the DataFrame as a table with custom headers
        st.write(df.drop(columns=['Updated At']), use_container_width=True)  # Exclude Updated At from table display
