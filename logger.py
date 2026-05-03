# logger.py
import pandas as pd
import os
from datetime import datetime

LOG_FILE = "logs.csv"

def log_row(emotion, score, blink_count=0):
    row = {
        "timestamp": datetime.now().isoformat(),
        "emotion": emotion,
        "score": float(score),
        "blink_count": int(blink_count)
    }
    df = pd.DataFrame([row])
    header = not os.path.exists(LOG_FILE)
    df.to_csv(LOG_FILE, mode="a", header=header, index=False)

def read_log(limit=1000):
    if not os.path.exists(LOG_FILE):
        return None
    df = pd.read_csv(LOG_FILE)
    return df.tail(limit)
