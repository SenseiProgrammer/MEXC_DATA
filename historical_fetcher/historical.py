# historical.py
from datetime import datetime
import time
import utils
import config
import api_client
import data_processor

# Initialize central logging
logger = utils.setup_logging()

def start_fetching():
    s_ts = utils.datetime_to_timestamp(config.START_DATE, "%Y-%m-%d")
    e_ts = utils.datetime_to_timestamp(config.END_DATE, "%Y-%m-%d")

    all_data = []
    current_ts = s_ts
    
    logger.info(f"Starting historical fetch for {config.SYMBOL} ({config.INTERVAL})")

    while current_ts < e_ts:
        data = api_client.get_mexc_klines(current_ts, e_ts)

        if data == "RETRY":
            continue

        if isinstance(data, list) and len(data) > 0:
            all_data.extend(data)
            last_ts = data[-1][0]
            current_ts = last_ts + 1
            logger.info(f"Progress: Fetched up to {datetime.fromtimestamp(last_ts/1000)}")
        else:
            logger.warning("Empty response received. Jumping 1 hour forward to bypass potential gap.")
            current_ts += (3600 * 1000) 

        time.sleep(0.5)

    data_processor.save_to_csv(all_data)
    logger.info("Historical fetch process completed.")

if __name__ == "__main__":
    start_fetching()