# historical.py
from datetime import datetime
import time
import utils
import config
import api_client
import data_processor

logger = utils.setup_logging()

def start_fetching():
    # Use your tweaked tm_type logic
    s_ts = utils.datetime_to_timestamp(config.START_DATE, tm_type="start")
    e_ts = utils.datetime_to_timestamp(config.END_DATE, tm_type="end")

    all_data = []
    current_ts = s_ts
    
    logger.info(f"Starting Bulk Fetch: {datetime.fromtimestamp(s_ts/1000)} to {datetime.fromtimestamp(e_ts/1000)}")

    # 1. Main Loop for bulk data
    # Stop slightly before the end to avoid the "live edge" empty response bug
    while current_ts < (e_ts - (5 * 60 * 1000)): 
        data = api_client.get_mexc_klines(current_ts, e_ts)
        if data == "RETRY": continue

        if isinstance(data, list) and len(data) > 0:
            all_data.extend(data)
            current_ts = data[-1][0] + 1
        else:
            current_ts += (3600 * 1000) 
        time.sleep(0.5)

    # 2. Targeted "Last Candle" Fetch
    # We explicitly request a window starting at the current_ts up to the e_ts
    logger.info("Performing separate fetch for the final candle...")
    last_candle_data = api_client.get_mexc_klines(current_ts, e_ts + 1000) # Overshoot by 1s
    
    if isinstance(last_candle_data, list) and len(last_candle_data) > 0:
        # Check to avoid duplicates
        for candle in last_candle_data:
            if not all_data or candle[0] > all_data[-1][0]:
                all_data.append(candle)
        logger.info(f"Final candle caught: {datetime.fromtimestamp(all_data[-1][0]/1000)}")

    data_processor.save_to_csv(all_data)
    logger.info("Process completed.")

if __name__ == "__main__":
    start_fetching()