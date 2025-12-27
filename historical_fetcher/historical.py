# historical.py
from datetime import datetime, timezone
import time
import utils
import config
import api_client
import data_processor

logger = utils.setup_logging()

def start_fetching():
    # Initial timestamps
    s_ts = utils.datetime_to_timestamp(config.START_DATE, tm_type="start")
    initial_e_ts = utils.datetime_to_timestamp(config.END_DATE, tm_type="end")

    all_data = []
    current_ts = s_ts
    
    logger.info(f"STARTING: Fetching {config.SYMBOL} ({config.INTERVAL})")

    # 1. Main Bulk Loop
    # We stop safely before the initial end time
    bulk_limit = initial_e_ts - (5 * 60 * 1000) 
    while current_ts < bulk_limit:
        data = api_client.get_mexc_klines(current_ts, initial_e_ts)
        if data == "RETRY": continue

        if isinstance(data, list) and len(data) > 0:
            all_data.extend(data)
            last_ts = data[-1][0]
            current_ts = last_ts + 1
            logger.info(f"PROGRESS: Synced up to {datetime.fromtimestamp(last_ts/1000, timezone.utc)} UTC")
        else:
            current_ts += (3600 * 1000) 
            if current_ts > initial_e_ts: break
        time.sleep(0.5)

    # 2. REAL-TIME SYNC: Re-check if a new candle finished while we were looping
    final_e_ts = initial_e_ts
    today_utc = datetime.now(timezone.utc).date()
    requested_date = datetime.strptime(config.END_DATE, "%Y-%m-%d").date()

    if requested_date >= today_utc:
        # Re-calculate the most recent closed candle right now
        now_ms = int(time.time() * 1000)
        five_min_ms = 5 * 60 * 1000
        current_actual_last_candle = (now_ms // five_min_ms) * five_min_ms
        
        if current_actual_last_candle > initial_e_ts:
            logger.info(f"SYNC: New candle detected! Updating end time to {datetime.fromtimestamp(current_actual_last_candle/1000, timezone.utc)} UTC")
            final_e_ts = current_actual_last_candle

    # 3. Targeted Final Fetch (covers from current_ts to the most recent final_e_ts)
    logger.info("FINALIZING: Fetching latest available closed data...")
    final_candles = api_client.get_mexc_klines(current_ts, final_e_ts + 1000)
    
    if isinstance(final_candles, list) and len(final_candles) > 0:
        for candle in final_candles:
            if not all_data or candle[0] > all_data[-1][0]:
                all_data.append(candle)
        final_time = datetime.fromtimestamp(all_data[-1][0], timezone.utc) if len(all_data[-1]) < 5 else datetime.fromtimestamp(all_data[-1][0]/1000, timezone.utc)
        logger.info(f"SUCCESS: Captured up to {final_time} UTC")

    data_processor.save_to_csv(all_data)
    logger.info("COMPLETE: Process finished.")

if __name__ == "__main__":
    start_fetching()