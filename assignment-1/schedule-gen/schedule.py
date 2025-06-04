import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
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
            if room.name == "magistrale":
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
        for t in range(self.start_time.hour, self.end_time.hour, self.slot_duration_hours):
            courses_by_time = self.get_courses_by_time()
            selected_course = random.choice(list(courses_by_time.get(datetime.time(hour=t))) + [None])
            selected_courses.append(selected_course)
        return [course for course in selected_courses if course is not None]

    def add_course(self, course: 'Course') -> bool:
        target_lecture_slot = course.lecture_slot

        if self.schedule[target_lecture_slot] is None:
            self.schedule[target_lecture_slot] = course
            print(f"Added course{course.id}")
            return True
        else:
            print(f"Slot {target_lecture_slot} is already occupied by course {self.schedule[target_lecture_slot].id}")
            return False

    def populate(self, num_courses: int) -> None:
        for course_id in range(num_courses):
            available_lecture_slots = [slot for slot in self.schedule.keys() if self.schedule[slot] is None]
            course = Course.generate_random_course(course_id, available_lecture_slots)
            self.add_course(course)

    def get_courses_by_time(self) -> dict:
        courses_by_time = {}
        for lecture_slot, course in self.schedule.items():
            if lecture_slot.start_time not in courses_by_time:
                courses_by_time[lecture_slot.start_time] = []
            courses_by_time[lecture_slot.start_time].append(course)
        return courses_by_time
    
    def visualize(self):
        if not self.rooms:
            print("Matplotlib: No rooms to visualize.")
            return
        if not self.schedule:
            print("Matplotlib: Schedule data is empty.")
            return

        fig, ax = plt.subplots(figsize=(15, len(self.rooms) * 0.6 + 2))

        room_names = [room.name for room in self.rooms.values()]
        y_ticks = np.arange(len(room_names))

        def time_to_float(t: datetime.time) -> float:
            return t.hour + t.minute / 60.0

        scheduled_items = []
        course_ids = sorted(list(set(course.id for course in self.schedule.values() if course is not None)))
        
        if course_ids:
            predefined_colors = list(mcolors.TABLEAU_COLORS.values())
            course_colors = {cid: predefined_colors[i % len(predefined_colors)] for i, cid in enumerate(course_ids)}

        for lecture_slot, course in self.schedule.items():
            if course is not None:
                scheduled_items.append({
                    "room": lecture_slot.room.name,
                    "start_time": time_to_float(lecture_slot.start_time),
                    "end_time": time_to_float(lecture_slot.end_time),
                    "course_id": course.id,
                    "label": f"C{course.id}"
                })

        if not scheduled_items:
            print("Matplotlib: No courses scheduled to visualize.")
            return
        
        for item in scheduled_items:
            namex = room_names.index(item["room"])
            duration = item["end_time"] - item["start_time"]
            color = course_colors.get(item["course_id"], 'gray')

            ax.barh(
                y=namex,
                width=duration,
                left=item["start_time"],
                height=0.6,
                label=item["label"] if item["course_id"] not in [bar.get_label() for bar in ax.containers if bar.get_label() == item["label"]] else "",
                color=color,
                edgecolor='black'
            )
            
            ax.text(
                item["start_time"] + duration / 2,
                namex,
                item["label"],
                ha='center',
                va='center',
                color='white',
                fontsize=8,
                fontweight='bold'
            )

        ax.set_yticks(y_ticks)
        ax.set_yticklabels(room_names)
        ax.set_xlabel("Time (Hour of Day)")
        ax.set_ylabel("Room")
        ax.set_title("Course Schedule")

        min_time = time_to_float(self.start_time)
        max_time = time_to_float(self.end_time)
        ax.set_xlim(min_time - 0.5, max_time + 0.5)
        
        x_tick_values = np.arange(int(min_time), int(max_time) + 1, 1)
        ax.set_xticks(x_tick_values)
        ax.set_xticklabels([f"{int(t):02d}:00" for t in x_tick_values])

        ax.invert_yaxis()
        plt.grid(True, axis='x', linestyle=':', alpha=0.7)

        plt.tight_layout(rect=[0, 0, 0.85, 1] if course_ids else [0,0,1,1])
        plt.show()
