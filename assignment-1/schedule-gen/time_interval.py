from datetime import time, timedelta, datetime

class TimeInterval:
    def __init__(self, start_time: time, duration: timedelta, type: str = "study") -> None:
        self.start_time = start_time
        # annoying
        self.end_time = (datetime.combine(datetime.min.date(), start_time) + duration).time()
        self.duration = duration
        self.type = type

    def __repr__(self) -> str:
        return f"TimeInterval(start_time={self.start_time}, duration={self.duration}, type={self.type})"
    