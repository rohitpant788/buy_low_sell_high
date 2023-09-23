import datetime
import yfinance as yf
import pandas as pd

from nifty_indices import nifty_indices


def calculate_rsi(data, period=14):
    close = data['Close']
    delta = close.diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    # Calculate initial average gains and losses
    avg_gains = gains.iloc[:period].mean()
    avg_losses = losses.iloc[:period].mean()

    rs_values = []

    for i in range(period, len(gains)):
        avg_gains = (avg_gains * (period - 1) + gains.iloc[i]) / period
        avg_losses = (avg_losses * (period - 1) + losses.iloc[i]) / period

        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        rs_values.append(rsi)

    return pd.Series(rs_values, index=close.index[period:])

def get_historical_data(stock_symbol, lookback_days=1000):
    try:

        # Check if the stock_symbol matches any Nifty index
        if stock_symbol in nifty_indices:
            stock_name = nifty_indices[stock_symbol]
        else:
            # If no match is found, add ".NS" to the symbol
            stock_name = stock_symbol + '.NS'

        end_date = datetime.date.today() - datetime.timedelta(days=1)
        start_date = end_date - datetime.timedelta(days=lookback_days)
        print(f'Getting historical data for {stock_name} from {start_date} to {end_date}')
        stock_data = pd.concat([yf.download(stock_name, start=start_date, end=end_date), yf.download(stock_name, interval='1m').iloc[-1:]])

        if stock_data.empty:
            print(f"No data available for {stock_name} starting from {start_date}.")
            return None

        # Calculate RSI using the calculate_rsi function
        stock_data['RSI'] = calculate_rsi(stock_data, period=14)

        # Calculate additional columns
        stock_data['% change for that Day'] = stock_data['Close'].pct_change() * 100
        stock_data['200 DMA (close)'] = stock_data['Close'].rolling(window=200).mean()
        stock_data['Price % from 200 DMA'] = ((stock_data['Close'] - stock_data['200 DMA (close)']) / stock_data['200 DMA (close)']) * 100
        stock_data['50 DMA (close)'] = stock_data['Close'].rolling(window=50).mean()
        stock_data['Price < 50DMA < 200DMA'] = (stock_data['Close'] < stock_data['50 DMA (close)']) & (stock_data['50 DMA (close)'] < stock_data['200 DMA (close)'])

        return stock_data
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def createCsv(stock_data, stock_name):
    # Select the columns you want to keep
    selected_columns = ['Close', '% change for that Day', '200 DMA (close)',
                        'Price % from 200 DMA', '50 DMA (close)',
                        'Price < 50DMA < 200DMA', 'RSI']
    # Save only the selected columns to the CSV file
    stock_data[selected_columns].to_csv(f"{stock_name}_historical_data_with_RSI.csv")