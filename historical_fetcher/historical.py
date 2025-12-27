# historical.py
from datetime import datetime
import time
import requests
import utils
import config
import api_client
import data_processor

# Initialize central logging
logger = utils.setup_logging()

def start_fetching():
    # 1. Get Server Time to avoid requesting "future" candles
    try:
        server_resp = requests.get(config.TIME_URL).json()
        server_now = server_resp['serverTime']
    except:
        server_now = int(time.time() * 1000)

    s_ts = utils.datetime_to_timestamp(config.START_DATE, "%Y-%m-%d")
    requested_e_ts = utils.datetime_to_timestamp(config.END_DATE, "%Y-%m-%d")
    
    # End time is whichever is earlier: your config or the current moment
    e_ts = min(requested_e_ts, server_now)

    all_data = []
    current_ts = s_ts
    
    logger.info(f"Starting historical fetch for {config.SYMBOL} ({config.INTERVAL})")

    while current_ts < (e_ts - 300000): # Stop 5 mins before end to avoid partial candles
        data = api_client.get_mexc_klines(current_ts, e_ts)

        if data == "RETRY":
            continue

        if isinstance(data, list) and len(data) > 0:
            all_data.extend(data)
            last_ts = data[-1][0]
            current_ts = last_ts + 1
            logger.info(f"Progress: Fetched up to {datetime.fromtimestamp(last_ts/1000)}")
        else:
            # If we are very close to the end, stop instead of jumping
            if (e_ts - current_ts) < 3600000: # Less than 1 hour left
                logger.info("Reached end of available data near current time.")
                break
            
            logger.warning(f"Gap at {datetime.fromtimestamp(current_ts/1000)}. Jumping 1 hour.")
            current_ts += (3600 * 1000) 

        time.sleep(0.5)

    data_processor.save_to_csv(all_data)
    logger.info("Historical fetch process completed.")

if __name__ == "__main__":
    start_fetching()