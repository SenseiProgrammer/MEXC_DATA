# data_processor.py
import pandas as pd
import logging
import config

logger = logging.getLogger(__name__) # Fixed: Dynamic name

def save_to_csv(all_candles):
    if not all_candles:
        logger.error("No data collected to save.")
        return

    try:
        df = pd.DataFrame(all_candles).iloc[:, :6]
        df.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
        df["Time"] = pd.to_datetime(df["Time"], unit='ms')
        
        cols = ["Open", "High", "Low", "Close", "Volume"]
        df[cols] = df[cols].apply(pd.to_numeric)
        
        df.to_csv(config.OUTPUT_PATH, index=False)
        logger.info(f"Successfully saved {len(df)} rows to {config.OUTPUT_PATH}")
    except Exception as e:
        logger.critical(f"Failed to process/save data: {e}")