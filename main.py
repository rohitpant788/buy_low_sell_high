import openpyxl
import pandas as pd
import streamlit as st

from config import WORKBOOK_FOR_BUY_LOW, WORKBOOK_V20_SHEET, WORKBOOK_V40_SHEET, WORKBOOK_ETF_SHEET
import get_nse_data

# Load the Excel workbook once at the beginning of the script
wb = openpyxl.load_workbook(WORKBOOK_FOR_BUY_LOW)


# Define your Streamlit app
def main():
    st.title("Buy Low Sell High")

    # Add a button to reload data
    if st.button("Reload Data"):
        update_workbook(WORKBOOK_V20_SHEET)
        update_workbook(WORKBOOK_V40_SHEET)
        update_workbook(WORKBOOK_ETF_SHEET)

    # Choose which sheet to display
    sheet_name = st.radio("Select Sheet", ["V20", "V40", "ETF"])
    column_headers, data = load_excel_data(sheet_name)

    # Display the data in a table using a DataFrame
    df = pd.DataFrame(data, columns=column_headers)
    st.write("Data:", df)

    # Create a text area below the table for displaying messages
    st.subheader("Log Messages")
    log_messages = st.text_area("Log Messages", value="", height=200)

    # Display log messages in the text area
    with st.echo():
        st.text("Your log messages go here.")
        # Append log messages to the text area
        log_messages += "\nYour new log message"  # Replace with your log message

    # Update log messages in the text area
    st.text_area("Log Messages", value=log_messages, height=200)


def load_excel_data(sheet_name):
    try:
        # Load and process Excel data as before
        sh1 = wb[sheet_name]

        # Get the total number of rows and columns
        max_row = sh1.max_row
        max_col = sh1.max_column

        # Create lists to store column headers and data
        column_headers = [sh1.cell(1, col).value for col in range(1, max_col + 1)]
        data = []

        for row in range(2, max_row + 1):  # Start from row 2 (skipping header)
            row_data = [sh1.cell(row, col).value for col in range(1, max_col + 1)]
            data.append(row_data)
        return column_headers, data
    except KeyError:
        st.error(f"Sheet {sheet_name} not found in the workbook.")


def update_workbook(sheet_name):
    try:
        sh1 = wb[sheet_name]
        # Update workbook as before
        # Append log messages to the log area using st.text

        # Get the total number of rows
        max_row = sh1.max_row

        # Create a list to store RSI and Price % from 200 DMA data and their corresponding row numbers
        rsi_data = []
        dma_data = []

        for row in range(2, max_row + 1):  # Start from row 2 (skipping header)
            # Read the symbol from the first column of each row
            symbol_cell = sh1.cell(row, 1)
            sym = symbol_cell.value

            # Add ".NS" to the symbol
            stock_symbol = sym + '.NS'

            # Get historical data
            candles = get_nse_data.get_historical_data(stock_symbol)
            df = pd.DataFrame(candles)

            # Append log messages for each row to the log area
            log_message = f'Processing Row {row} for symbol {sym}'
            st.text(log_message)

            if not df.empty:
                # Get the last row of the DataFrame
                last_row = df.iloc[-1]

                # Update cells in the current row with relevant data
                cell_values = [
                    last_row['Close'],
                    last_row['% change for that Day'],
                    last_row['200 DMA (close)'],
                    last_row['Price % from 200 DMA'],
                    last_row['50 DMA (close)'],
                    last_row['Price < 50DMA < 200DMA'],
                    last_row['RSI']
                ]

                for col, value in enumerate(cell_values, start=2):
                    sh1.cell(row, col).value = value

                # Store RSI and Price % from 200 DMA values and row number in the lists
                rsi_data.append((last_row['RSI'], row))
                dma_data.append((last_row['Price % from 200 DMA'], row))

        # Rank the stocks based on RSI (ascending order)
        rsi_data.sort(key=lambda x: x[0])
        for rank, (rsi, row_num) in enumerate(rsi_data, start=1):
            sh1.cell(row_num, 9).value = rank  # Add RSI Rank in a new column (column I)

        # Rank the stocks based on Price % from 200 DMA (ascending order)
        dma_data.sort(key=lambda x: x[0])
        for rank, (dma, row_num) in enumerate(dma_data, start=1):
            sh1.cell(row_num, 10).value = rank  # Add 200 DMA Rank in a new column (column J)

        # Save the updated workbook
        wb.save(WORKBOOK_FOR_BUY_LOW)
    except KeyError:
        st.error(f"Sheet {sheet_name} not found in the workbook.")


if __name__ == "__main__":
    main()
