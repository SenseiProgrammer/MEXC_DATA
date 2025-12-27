import logging
import sys
from config import LOGFILE
from datetime import datetime

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

def datetime_to_timestamp(date, date_format="%Y-%m-%d"):
    return int(datetime.strptime(date, date_format).timestamp() * 1000)