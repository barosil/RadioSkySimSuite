from datetime import datetime, timedelta

def split_15min(timestamp: datetime):
    """
    Returns a list of timestamps covering 15 minutes
    """
    return [timestamp + timedelta(minutes=i) for i in range(15)]