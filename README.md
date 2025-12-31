# 📈 Buy Low Sell High - Stock Analysis Tool

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://buylowsellhigh-mhfnsu6mkzvuzhufewzsdq.streamlit.app/)

A powerful **Streamlit-based stock market analysis application** designed to help investors identify potential buying opportunities in the Indian Stock Market (NSE). The tool automates technical screening using **RSI**, **Moving Averages (50 & 200 DMA)**, and **Multi-Year Breakout** patterns.

🔗 **Live Demo:** [https://buylowsellhigh-mhfnsu6mkzvuzhufewzsdq.streamlit.app/](https://buylowsellhigh-mhfnsu6mkzvuzhufewzsdq.streamlit.app/)

---

## 🚀 Key Features

### 1. 📊 Interactive Watchlist Dashboard
Monitor predefined watchlists (Indices, Nifty 50, Nifty 100, ETFs, etc.) with real-time technical metrics:
- **Price < 50DMA < 200DMA**: Automatically flags stocks in a potential "value zone".
- **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions with ranking.
- **200 DMA Analysis**: Shows % distance from the 200-day moving average and ranks stocks by "dip" potential.
- **Direct Charts**: Clickable stock symbols link directly to **TradingView** charts.

### 2. 💥 Multi-Year Breakout Analyzer
A dedicated tool to find stocks breaking out of long-term consolidation ranges.
- **Customizable Logic**: Set your own **Years Gap** (1-10 years) and **Buffer** %.
- **Retrospective Analysis**: Look back `N` weeks to see past breakouts.
- **Flexible Input**: Upload a CSV of symbols or manually enter a comma-separated list.
- **Smart Caching**: caches historical data to optimize performance and respect API limits.

### 3. 🛡️ Admin Watchlist Management
A password-protected admin section to manage the application's data.
- **CRUD Operations**: Create, Update, Delete watchlists.
- **Bulk Import**: Add stocks via CSV upload.
- **Auto-Refresh**: Background scheduler keeps data updated (configurable).

---

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Data Source**: [yfinance](https://pypi.org/project/yfinance/) (Yahoo Finance via `get_nse_data.py`)
- **Database**: [SQLite](https://www.sqlite.org/) (Local file-based storage)
- **Data Processing**: Pandas, NumPy
- **Authentication**: `streamlit-authenticator`
- **Scheduling**: `APScheduler`

---

## 📂 Project Structure

```text
buy_low_sell_high/
├── main.py                    # 🟢 Entry point for the Streamlit app
├── watchlist_display.py       # 📉 Logic for displaying and ranking watchlist data
├── watchlist_management.py    # ⚙️ Admin CRUD operations for watchlists
├── multi_year_breakout.py     # 🚀 Core logic for breakout detection
├── get_nse_data.py            # 📡 Data fetching wrapper for NSE stocks & Indices
├── update_data.py             # 🔄 Database update routines
├── scheduler.py               # ⏰ Background job for periodic data refreshes
├── config.py                  # 🔧 Configuration constants
├── buy_low_sell_high.db       # 🗄️ SQLite Database
└── requirements.txt           # 📦 Python dependencies
```

---

## ⚡ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd buy_low_sell_high
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run main.py
   ```

---

## 🔑 Authentication

The **Manage Watchlists** section is protected by login credentials.

*Note: Passwords are securely hashed and stored in `hashed_pw.pkl`.*

---

## 🔄 Data Updates

The application includes a background scheduler (`scheduler.py`) configured to refresh stock data automatically.
- **Manual Trigger**: Admins can trigger updates for specific watchlists in the Management tab.
- **Auto-Update**: Runs periodically to fetch the latest Close prices, RSI, and DMA values.

---

## 📝 Configuration

- **Database Path**: defined in `config.py`.
- **Log Level**: Configurable in `logging_utils.py`.
- **Nifty Indices**: Mappings for index symbols are in `nifty_indices.py`.

---

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
