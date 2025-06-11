import datetime
from course import Course
from room import Room
from lecture_slot import LectureSlot
import random

class Schedule:
    def __init__(self, rooms: dict[str, Room]) -> None:
        self.start_time = datetime.time(8, 0)
        self.end_time = datetime.time(18, 0)
        self.rooms = rooms
        self.schedule = {}
        self.slot_duration_hours = 2
        
        for room in self.rooms.values():
            if room.name == "magistrale" or room.name == "library" or room.name == "computerhall":
                continue
            current_hour = self.start_time.hour
            while current_hour + self.slot_duration_hours <= self.end_time.hour:
                start_time = datetime.time(current_hour, 0)
                end_time = datetime.time(current_hour + self.slot_duration_hours, 0)
                lecture_slot = LectureSlot(room, start_time, end_time)
                self.schedule[lecture_slot] = None
                current_hour += self.slot_duration_hours

    def generate_random_enrollment(self) -> list[Course]:
        selected_courses = []
        courses_by_time = self.get_courses_by_time()
        # Continue until there is at least one course in the selected courses
        # This is the only way of I could think of generating a schedule that is the same as uniformly sampling from all possible non-conflicting non-empty schedules.
        while not any(selected_courses):
            for time_slot in courses_by_time.keys():
                selected_course = random.choice(courses_by_time[time_slot] + [None])
                selected_courses.append(selected_course)
        return [course for course in selected_courses if course is not None]

    def add_course(self, course: 'Course') -> bool:
        target_lecture_slot = course.lecture_slot
        if self.schedule[target_lecture_slot] is None:
            self.schedule[target_lecture_slot] = course
            return True
        else:
            print(f"Slot {target_lecture_slot} is already occupied by course {self.schedule[target_lecture_slot].id}")
            return False

    def populate(self, num_courses: int) -> None:
        for course_id in range(num_courses):
            available_lecture_slots = [slot for slot in self.schedule.keys() if self.schedule[slot] is None]
            course = Course.generate_random_course(course_id, available_lecture_slots)
            self.add_course(course)

    def get_courses_by_time(self) -> dict[datetime.time, list[Course]]:
        courses_by_time = {}
        for lecture_slot, course in self.schedule.items():
            if course is not None:
                if lecture_slot.start_time not in courses_by_time:
                    courses_by_time[lecture_slot.start_time] = []
                courses_by_time[lecture_slot.start_time].append(course)
        return courses_by_time

if __name__ == "__main__":
    pass