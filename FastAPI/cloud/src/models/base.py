from sqlalchemy.orm import declarative_base
from datetime import datetime, date, time, timedelta

Base = declarative_base()

def default_tomorrow_9pm():
    """Return tomorrow 9:00 PM as datetime"""
    tomorrow = date.today() + timedelta(days=1)
    return datetime.combine(tomorrow, time(21, 0))  # 9:00 PM