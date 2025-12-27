# config.py

# --- Collection Settings ---
SYMBOL = "SOLUSDT"
INTERVAL = "5m"
START_DATE = "2025-11-01"
END_DATE = "2025-12-27"
BASE_URL = "https://api.mexc.com/api/v3/klines"
TIME_URL = "https://api.mexc.com/api/v3/time" # New: for server sync
LOGFILE = "fetcher.log"
OUTPUT_PATH = "SOLUSDT_5m_historical_data.csv"