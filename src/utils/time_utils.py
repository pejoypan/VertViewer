from datetime import datetime

def now_time() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")