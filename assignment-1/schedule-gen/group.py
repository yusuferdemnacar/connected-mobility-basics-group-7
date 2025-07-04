from pathlib import Path
from course import Course
from lecture_slot import LectureSlot
import datetime
from room import Room

class Group:
    def __init__(self, id: int, nrof_hosts: int = 1, enrollment: list[Course] = None) -> None:
        self.id = id
        self.nrof_hosts = nrof_hosts
        self.enrollment = enrollment

    def generate_route_file(self, file_path: Path, initial_x: float, initial_y: float) -> None:
        file_path.mkdir(parents=True, exist_ok=True)
        with open(file_path / f"lecturetaker_{self.id}_route.wkt", "w") as file:
            file.write("LINESTRING (")
            self.enrollment.sort(key=lambda x: x.lecture_slot.start_time)
            for i, course in enumerate(self.enrollment):
                if course.lecture_slot.room.name == "magistrale":
                    file.write(f"{self.enrollment[i - 1].lecture_slot.room.door_outside_x} {self.enrollment[i - 1].lecture_slot.room.door_outside_y}, ")
                else:
                    file.write(f"{course.lecture_slot.room.door_inside_x} {course.lecture_slot.room.door_inside_y}, ")
            file.write(f"{initial_x} {initial_y})\n")

    def generate_schedule_file(self, file_path: Path) -> None:
        self.enrollment.sort(key=lambda x: x.lecture_slot.start_time)
        file_path.mkdir(parents=True, exist_ok=True)
        with open(file_path / f"lecturetaker_{self.id}_schedule.txt", "w") as file:
            for course in self.enrollment:
                file.write(f"{course.lecture_slot.room.name}\n")

    def fill_with_idle_period(self, idle_room: Room) -> None:
        self.enrollment.sort(key=lambda x: x.lecture_slot.start_time)
        first_course = self.enrollment[0] if self.enrollment else None
        last_course = self.enrollment[-1] if self.enrollment else None
        for time_slot in range(8, 18, 2):
            if ((time_slot > first_course.lecture_slot.start_time.hour) and 
                (time_slot < last_course.lecture_slot.start_time.hour) and 
                not any(course.lecture_slot.start_time.hour == time_slot for course in self.enrollment)):
                    self.enrollment.append(
                        Course(
                            id="Idle",
                            lecture_slot=LectureSlot(
                                room=idle_room,
                                start_time=datetime.time(hour=time_slot, minute=0),
                                end_time=datetime.time(hour=time_slot + 2, minute=0)
                            )
                        )
                    )

    # TODO: make all settings configurable
    @staticmethod
    def generate_group_settings(groups: list, group_data_dir: Path) -> list[str]:
        lines = []
        lines.append(f"\nScenario.nrofHostGroups = {len(groups) + 1}\n\n")
        for group in groups:
            enrollment_by_time = sorted(group.enrollment, key=lambda x: x.lecture_slot.start_time)
            start_time = enrollment_by_time[0].lecture_slot.start_time.hour
            end_time = enrollment_by_time[-1].lecture_slot.end_time.hour
            lines.append(f"# Group{group.id} settings\n")
            lines.append(f"Group{group.id}.groupID = lecturetaker_{group.id}_\n")
            lines.append(f"Group{group.id}.nrofHosts = {group.nrof_hosts}\n")
            lines.append(f"Group{group.id}.movementModel = LectureTakerMovement\n")
            lines.append(f"Group{group.id}.routeFile = {group_data_dir}/lecturetaker_{group.id}_route.wkt\n")
            lines.append(f"Group{group.id}.routeType = 1\n")
            lines.append(f"Group{group.id}.routeFirstStop = 0\n")
            lines.append(f"Group{group.id}.startTime = {(start_time - 8) * 60 * 60}\n")
            lines.append(f"Group{group.id}.endTime = {(end_time - 8) * 60 * 60}\n")
            lines.append(f"Group{group.id}.waitTime = 600, 1800\n")
            lines.append(f"Group{group.id}.router = SprayAndWaitRouter\n")
            lines.append(f"Group{group.id}.msgTtl = 8\n")
            lines.append(f"Group{group.id}.speed = 0.5, 1.5\n")
            lines.append(f"Group{group.id}.nrofInterfaces = 1\n")
            lines.append(f"Group{group.id}.interface1 = bluetoothInterface\n")
            lines.append("\n")
        return lines

if __name__ == "__main__":
    pass