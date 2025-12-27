# data_processor.py
import pandas as pd
import logging
import config

logger = logging.getLogger(__name__)

def save_to_csv(all_candles):
    """
    Processes the raw candle data, applies timezone conversions, 
    calculates candle types, and saves to CSV.
    """
    if not all_candles:
        logger.error("No data collected to save.")
        return

    try:
        # 1. Create the base DataFrame
        df = pd.DataFrame(all_candles).iloc[:, :6]
        df.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]

        # 2. Convert price/volume columns to numeric for calculations
        cols = ["Open", "High", "Low", "Close", "Volume"]
        df[cols] = df[cols].apply(pd.to_numeric)

        # 3. Handle Time Columns
        # Convert raw ms timestamp to a UTC datetime object
        df["Time"] = pd.to_datetime(df["Time"], unit='ms')
        
        # Create UTC_TIME column and insert it right after the main Time column
        # At this stage, df["Time"] is UTC
        df.insert(1, "UTC_TIME", df["Time"])
        
        # Now convert the main "Time" column to IST (Asia/Kolkata)
        df["Time"] = df["Time"].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        
        # Remove the timezone offset string (+05:30) for a clean CSV format
        df["Time"] = df["Time"].dt.tz_localize(None)
        df["UTC_TIME"] = df["UTC_TIME"].dt.tz_localize(None)

        # 4. Add CANDLE_TYPE at the end
        # Bullish if Close > Open, Bearish otherwise
        df["CANDLE_TYPE"] = df.apply(
            lambda x: "Bullish" if x["Close"] > x["Open"] else "Bearish", 
            axis=1
        )

        # 5. Save to CSV
        df.to_csv(config.OUTPUT_PATH, index=False)
        logger.info(f"Successfully saved {len(df)} rows to {config.OUTPUT_PATH}")
        logger.info("Sample Data:\n" + df.tail().to_string())
    except Exception as e:
        logger.error(f"Failed to save data to CSV: {e}")