from pathlib import Path
import matplotlib.pyplot as plt
from course import Course
from lecture_slot import LectureSlot
import datetime
from room import Room

class Group:
    def __init__(self, id: int, nrof_hosts: int = 1, enrollment: list = None):
        self.id = id
        self.nrof_hosts = nrof_hosts
        self.enrollment = enrollment

    def generate_route_file(self, file_path: Path, initial_x: float, initial_y: float):
        file_path.mkdir(parents=True, exist_ok=True)
        with open(file_path / f"group{self.id}_route.wkt", "w") as file:
            file.write("LINESTRING (")
            self.enrollment.sort(key=lambda x: x.lecture_slot.start_time)
            for course in self.enrollment:
                file.write(f"{course.lecture_slot.room.door_inside_x} {course.lecture_slot.room.door_inside_y}, ")
            file.write(f"{initial_x} {initial_y})\n")

    def generate_room_sequence_file(self, file_path: Path):
        self.enrollment.sort(key=lambda x: x.lecture_slot.start_time)
        file_path.mkdir(parents=True, exist_ok=True)
        with open(file_path / f"group{self.id}_room_sequence.txt", "w") as file:
            for course in self.enrollment:
                file.write(f"{course.lecture_slot.room.name}\n")

    def fill_with_idle_period(self, idle_room: Room):
        self.enrollment.sort(key=lambda x: x.lecture_slot.start_time)
        for time_slot in range(8, 18, 2):
            if not any(
                course.lecture_slot.start_time.hour == time_slot and course.lecture_slot.end_time.hour == time_slot + 2
                for course in self.enrollment
            ):
                special_course = Course("Idle", LectureSlot(
                    room=idle_room,
                    start_time=datetime.time(hour=time_slot),
                    end_time=datetime.time(hour=time_slot + 2)
                ))
                self.enrollment.append(special_course)

    # TODO: make all settings configurable
    @staticmethod
    def generate_group_settings(groups: list, group_data_dir: Path) -> list:
        lines = []
        lines.append(f"\nScenario.nrofHostGroups = {len(groups)}\n\n")
        for group in groups:
            lines.append(f"# Group{group.id} settings\n")
            lines.append(f"Group{group.id}.groupID = group{group.id}\n")
            lines.append(f"Group{group.id}.nrofHosts = {group.nrof_hosts}\n")
            lines.append(f"Group{group.id}.movementModel = LectureTakerMovement\n")
            lines.append(f"Group{group.id}.routeFile = {group_data_dir}/group{group.id}_route.wkt\n")
            lines.append(f"Group{group.id}.routeType = 1\n")
            lines.append(f"Group{group.id}.routeFirstStop = 0\n")
            lines.append(f"Group{group.id}.router = EpidemicRouter\n")
            lines.append(f"Group{group.id}.bufferSize = 5M\n")
            lines.append(f"Group{group.id}.speed = 0.5, 1.5\n")
            lines.append(f"Group{group.id}.nrofInterfaces = 1\n")
            lines.append(f"Group{group.id}.interface1 = btInterface\n")
            lines.append(f"Group{group.id}.msgTtl = 300\n")
            lines.append("\n")
        return lines
    
    @staticmethod
    def visualize(groups: list):
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_title("Course Schedule for Each Group")
        ax.set_xlim(8, 18)
        ax.set_xlabel("Time Slot (Hour of Day)")
        ax.set_ylabel("Groups")

        group_keys = list(range(1, len(groups) + 1))
        
        ax.set_yticks(range(len(group_keys))) 
        ax.set_yticklabels(group_keys) 
        
        magistrale_color = 'skyblue'
        other_course_color = 'salmon'
        
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, color=other_course_color, label='Regular Course'),
            plt.Rectangle((0, 0), 1, 1, color=magistrale_color, label='Idle')
        ]
        
        for group_idx, group in enumerate(groups):
            courses = group.enrollment
            for course in courses:
                start_time_float = course.lecture_slot.start_time.hour + course.lecture_slot.start_time.minute / 60
                end_time_float = course.lecture_slot.end_time.hour + course.lecture_slot.end_time.minute / 60
                duration = end_time_float - start_time_float
                
                bar_color = magistrale_color if course.id == "Idle" else other_course_color
                
                ax.barh(group_idx, duration, left=start_time_float, height=0.6, color=bar_color, edgecolor='black')
                
                text_x = start_time_float + duration / 2
                text_y = group_idx 
                ax.text(text_x, text_y, course.lecture_slot.room.name if course.lecture_slot.room.name else "N/A", 
                        ha='center', va='center', color='black', fontsize=8)

        ax.legend(handles=legend_elements)
        plt.grid(True, axis='x')
        plt.tight_layout()
        plt.show()