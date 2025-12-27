# api_client.py
import requests
import time
import logging
import config

logger = logging.getLogger(__name__) # Fixed: Dynamic name

def get_mexc_klines(start_time, end_time):
    params = {
        "symbol": config.SYMBOL,
        "interval": config.INTERVAL,
        "startTime": start_time,
        "endTime": end_time,
        "limit": 1000
    }
    
    try:
        response = requests.get(config.BASE_URL, params=params, timeout=15)
        
        if response.status_code == 429:
            logger.warning("Rate limit (429) hit. Sleeping 10s...")
            time.sleep(10)
            return "RETRY"
            
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None