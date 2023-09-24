from datetime import datetime

import pandas as pd
import pytz
import streamlit as st

def calculate_ranks(df):
    # Calculate RSI Rank (ascending order)
    df['RSI Rank'] = df['RSI'].rank(ascending=True, method='min')
    # Calculate DMA 200 Rank (ascending order)
    df['200 DMA Rank'] = df['% Away from 200 DMA'].rank(ascending=True, method='min')
    return df


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

        custom_column_names = {
            'stock_symbol': 'Symbol',
            'stock_price': 'Price',
            'price_50dma_200dma': 'Price < 50DMA <200DMA',
            'rsi': 'RSI',
            'per_change': '% Change',
            'dma_200_close': '200 DMA Close',
            'percent_away_from_dma_200': '% Away from 200 DMA',
            'dma_50_close': '50 DMA Close',
            'updated_at': 'Updated At'  # Rename the updated_at column
        }
        # Define a dictionary to map original column names to custom names

        # Rename the columns using the custom names
        df = df.rename(columns=custom_column_names)

        # Calculate RSI Rank and DMA 200 Rank and update them in the DataFrame
        df = calculate_ranks(df)

        # Rearrange column order as per your requirement
        column_order = ['Symbol', 'Price', 'Price < 50DMA <200DMA', 'RSI Rank', '200 DMA Rank', 'RSI']
        remaining_columns = [col for col in df.columns if col not in column_order]
        column_order += remaining_columns

        df = df[column_order]

        # Assuming df['Updated At'].iloc[0] is a string representation of a timestamp
        timestamp_str = df['Updated At'].iloc[0]

        try:
            # Split the timestamp string to separate milliseconds and time zone offset
            timestamp_parts = timestamp_str.split(".")
            timestamp_without_milliseconds = timestamp_parts[0]
            milliseconds_and_timezone = timestamp_parts[1]  # Contains milliseconds and time zone offset

            # Convert the string without milliseconds to a datetime object
            timestamp_datetime = datetime.strptime(timestamp_without_milliseconds, "%Y-%m-%d %H:%M:%S")

            # Extract milliseconds from the milliseconds_and_timezone string
            milliseconds = int(milliseconds_and_timezone.split("+")[0])

            # Truncate milliseconds to the maximum allowed microseconds value (999999)
            microseconds = min(milliseconds * 1000, 999999)

            # Add the extracted microseconds to the datetime object
            timestamp_datetime = timestamp_datetime.replace(microsecond=microseconds)

            # Convert the datetime object to UTC timezone
            utc_timezone = pytz.timezone('UTC')
            timestamp_in_utc = utc_timezone.localize(timestamp_datetime)

            # Convert UTC timestamp to IST timezone
            ist_timezone = pytz.timezone('Asia/Kolkata')
            timestamp_in_ist = timestamp_in_utc.astimezone(ist_timezone)

            # Format the timestamp in a more readable way
            formatted_time = timestamp_in_ist.strftime("%Y-%m-%d %I:%M:%S %p")

            # Display the formatted timestamp
            st.markdown(f"### Watchlist Data: Updated At {formatted_time} (Asia/Kolkata)")
            st.markdown(f"### Watchlist Data: Updated At  {timestamp_str} (UTC)")

            # Display the DataFrame as a table with custom headers
            st.write(df.drop(columns=['Updated At']), use_container_width=True)  # Exclude Updated At from table display

        except ValueError as e:
            st.error("Error: Invalid timestamp format.")
            st.write(e)
        except Exception as e:
            st.error("An error occurred while processing the timestamp.")
            st.write(e)
