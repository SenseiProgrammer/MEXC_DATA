# historical.py
from datetime import datetime
import time
import utils
import config
import api_client
import data_processor

# Initialize central logging using the utility setup
logger = utils.setup_logging()
def start_fetching():
    # Pass 'start' and 'end' to use the specific rounding logic
    s_ts = utils.datetime_to_timestamp(config.START_DATE, tm_type="start")
    e_ts = utils.datetime_to_timestamp(config.END_DATE, tm_type="end")

    all_data = []
    current_ts = s_ts
    
    logger.info(f"Starting fetch. Target Range: {datetime.fromtimestamp(s_ts/1000)} to {datetime.fromtimestamp(e_ts/1000)}")

    while current_ts < e_ts:
        data = api_client.get_mexc_klines(current_ts, e_ts)
        # Fetch a chunk of data (up to 1000 candles)
        data = api_client.get_mexc_klines(current_ts, e_ts)

        if data == "RETRY":
            continue

        if isinstance(data, list) and len(data) > 0:
            all_data.extend(data)
            
            # Update the pointer to 1ms after the last received candle
            last_ts = data[-1][0]
            current_ts = last_ts + 1
            logger.info(f"Progress: Fetched up to {datetime.fromtimestamp(last_ts/1000)}")
        else:
            # 3. Handle Gaps or the Live Edge
            # If we are within 1 hour of our target end time, we finish.
            if (e_ts - current_ts) < (60 * 60 * 1000):
                logger.info("Reached the target end time or live edge. Finalizing...")
                break
            
            # Otherwise, jump forward 1 hour to bypass potential exchange data gaps
            logger.warning(f"Empty response at {datetime.fromtimestamp(current_ts/1000)}. Jumping 1 hour.")
            current_ts += (3600 * 1000) 

        # Respect API rate limits
        time.sleep(0.5)

    # 4. Save the stitched results to the CSV defined in config
    data_processor.save_to_csv(all_data)
    logger.info("Historical fetch process completed successfully.")

if __name__ == "__main__":
    start_fetching()