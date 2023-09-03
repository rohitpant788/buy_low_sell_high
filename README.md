# Stock Data Analysis Tool

This Python script is designed to update an Excel workbook with various stock data metrics, including the Relative Strength Index (RSI) and the rank based on the Price % from 200 DMA.

## Prerequisites

Before using this tool, make sure you have the following prerequisites installed on your system:

- Python 3.x
- `openpyxl` library
- `pandas` library
- `config.py` file (containing workbook and sheet names)
- `get_nse_data` module (for downloading historical stock data)

## Usage

1. Ensure that you have the required libraries installed:

   ```bash
   pip install openpyxl pandas


# Worksheet Constants
WORKBOOK_FOR_BUY_LOW = 'buy_low.xlsx'
WORKBOOK_V20_SHEET = 'V20'
WORKBOOK_V40_SHEET = 'V40'
WORKBOOK_ETF_SHEET = 'ETF'


#Run the script:
```bash
python main.py
```

The script will load the specified Excel workbook and update it with the latest stock data, including RSI and rankings.

#Functionality
- The script iterates through specified sheets in the Excel workbook.
- For each stock symbol in the sheet, it adds ".NS" to the symbol (for NSE stocks) and fetches historical stock data.
- It calculates various metrics, including RSI and Price % from 200 DMA, and updates the Excel sheet with the latest data.
- The script ranks stocks based on RSI and Price % from 200 DMA, updating the corresponding columns.

#Notes
- Ensure that you have access to historical stock price data for accurate calculations.
- The script may require adjustments if you are using a different data source or calculation parameters.
- Always verify the data and results for accuracy and consistency with your requirements.

Feel free to adapt and modify this script as needed for your specific use case.