from datetime import datetime

def now_time() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_time_log() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")