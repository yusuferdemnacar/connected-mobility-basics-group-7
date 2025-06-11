from datetime import time, timedelta, datetime
import random
from time_interval import TimeInterval
from room import Room
class StudyPlan:
    def __init__(self, start_time: time = time(8, 0), duration: timedelta = timedelta(hours=12), room: str = "library", intervals: list[TimeInterval] = None) -> None:
        self.start_time = start_time
        self.end_time = (datetime.combine(datetime.min.date(), start_time) + duration).time()
        self.duration = duration
        self.room = room
        self.intervals = intervals

    @staticmethod
    def generate_study_room_assignment_file(study_plans: list['StudyPlan'], file_path: str) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as file:
            for i, study_plan in enumerate(study_plans):
                file.write(f"{i + 1}, {study_plan.room.name}\n")

    def generate_route_file(self, file_path: str, initial_x: float, initial_y: float) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as file:
            file.write("LINESTRING (")
            for interval in self.intervals:
                if interval.type == "study":
                    file.write(f"{self.room.door_inside_x} {self.room.door_inside_y}, ")
                elif interval.type == "break":
                    file.write(f"{self.room.door_outside_x} {self.room.door_outside_y}, ")
            file.write(f"{initial_x} {initial_y})\n")
    
    def generate_timetable_file(self, file_path: str) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as file:
            # each line holds an integer corresponding to simulator time (seconds)
            # the start and end times are from 8 am so we subtract 8 hours
            first_end_time = self.intervals[0].end_time.hour * 3600 + self.intervals[0].end_time.minute * 60
            first_end_time -= 8 * 3600
            file.write(f"{first_end_time}\n")
            for interval in self.intervals[1:]:
                end_time = interval.end_time.hour * 3600 + interval.end_time.minute * 60
                end_time -= 8 * 3600
                file.write(f"{end_time}\n")

    @staticmethod
    def random_study_plan(rooms: list[Room]) -> 'StudyPlan':
        room = random.choice(rooms)
        intervals = []
        nrof_sessions = random.randint(1, 5)
        first_session_duration = random.randint(30, 90)
        intervals.append(TimeInterval(time(8, 0), timedelta(minutes=first_session_duration), "study"))
        for _ in range(nrof_sessions - 1):
            break_duration = random.randint(5, 20)
            intervals.append(TimeInterval(intervals[-1].end_time, timedelta(minutes=break_duration), "break"))
            session_duration = random.randint(30, 90)
            intervals.append(TimeInterval(intervals[-1].end_time, timedelta(minutes=session_duration), "study"))
        
        total_duration = sum((interval.duration for interval in intervals), start=timedelta())
        offset_minutes = random.randint(0, (int) ((timedelta(hours=12) - total_duration).total_seconds()) // 60)
        
        # Offset start and end times of intervals with the random offset
        for interval in intervals:
            interval.start_time = (datetime.combine(datetime.min.date(), interval.start_time) + timedelta(minutes=offset_minutes)).time()
            interval.end_time = (datetime.combine(datetime.min.date(), interval.end_time) + timedelta(minutes=offset_minutes)).time()

        return StudyPlan(intervals[0].start_time, total_duration, room, intervals)

if __name__ == "__main__":
    pass