# utils.py
import logging
import sys
import time
from config import LOGFILE
from datetime import datetime, timedelta

def setup_logging():
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(LOGFILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("MEXC-Fetcher")

def datetime_to_timestamp(date_str, date_format="%Y-%m-%d", tm_type="start"):
    """
    Converts date string to ms timestamp. 
    'start' = 00:00:00. 
    'end' today = last closed 5m candle.
    'end' past = 23:55:00.
    """
    input_date = datetime.strptime(date_str, date_format).date()
    now_utc = datetime.utcnow()
    today_utc = now_utc.date()

    if tm_type == "end":
        if input_date >= today_utc:
            # Round current UTC time down to the last 5-minute candle
            now_ms = int(time.time() * 1000)
            five_min_ms = 5 * 60 * 1000
            return (now_ms // five_min_ms) * five_min_ms
        else:
            # Past dates: set to 23:55:00
            past_dt = datetime.combine(input_date, datetime.min.time()) + timedelta(hours=23, minutes=55)
            return int(past_dt.timestamp() * 1000)
    else:
        # Start time: 00:00:00
        start_dt = datetime.combine(input_date, datetime.min.time())
        return int(start_dt.timestamp() * 1000)