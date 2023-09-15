import openpyxl
import pandas as pd
import streamlit as st
import logging

from config import WORKBOOK_FOR_BUY_LOW, WORKBOOK_V20_SHEET, WORKBOOK_V40_SHEET, WORKBOOK_ETF_SHEET
import get_nse_data

# Configure logging
from logging_utils import get_log_messages, update_log_messages
from update_data import update_workbook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the Excel workbook once at the beginning of the script
wb = openpyxl.load_workbook(WORKBOOK_FOR_BUY_LOW)

# Define your Streamlit app
def main():
    st.title("Buy Low Sell High")

    # Add a button to reload data
    if st.button("Reload Data"):
        with st.spinner("Reloading data..."):
            update_workbook(wb,WORKBOOK_V20_SHEET)
            update_workbook(wb,WORKBOOK_V40_SHEET)
            update_workbook(wb,WORKBOOK_ETF_SHEET)

    # Choose which sheet to display
    sheet_name = st.radio("Select Sheet", ["V20", "V40", "ETF"])
    column_headers, data = load_excel_data(sheet_name)

    # Display the data in a table using a DataFrame
    df = pd.DataFrame(data, columns=column_headers)
    st.write("Data:", df)

    # Display log messages
    st.subheader("Log Messages")
    log_messages = get_log_messages()
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

if __name__ == "__main__":
    main()
