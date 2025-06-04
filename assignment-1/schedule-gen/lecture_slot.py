import datetime
from room import Room

class LectureSlot:
    def __init__(self, room: Room, start_time: datetime.time, end_time: datetime.time):
        self.room = room
        self.start_time = start_time
        self.end_time = end_time
    
    def __hash__(self):
        return hash((self.room, self.start_time, self.end_time))
    
    def __repr__(self):
        return f"LectureSlot(room='{self.room}', start_time='{self.start_time.strftime('%H:%M')}', end_time='{self.end_time.strftime('%H:%M')}')"