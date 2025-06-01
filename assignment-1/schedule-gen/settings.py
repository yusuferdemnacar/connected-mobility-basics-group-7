from course import Course
from group import Group
from lecture_slot import LectureSlot
from room import Room
from schedule import Schedule
from pathlib import Path

class Settings:
    def __init__(self, file_path: Path):
        self.file_path = file_path
    
    def insert_group_settings(self, groups: list[Group]) -> None:

        insertion_lines = Group.generate_group_settings(groups)

        with open(self.file_path) as file:
            content = file.readlines()
            start_index = content.index("## Group settings (start)\n") + 1
            end_index = content.index("## Group settings (end)\n")
            content = content[:start_index] + insertion_lines + content[end_index:]
        with open(self.file_path, "w") as file:
            file.writelines(content)

    def insert_room_settings(self, rooms: list[Room]) -> None:

        insertion_lines = Room.generate_room_settings(rooms)

        with open(self.file_path) as file:
            content = file.readlines()
            start_index = content.index("## Room settings (start)\n") + 1
            end_index = content.index("## Room settings (end)\n")
            content = content[:start_index] + insertion_lines + content[end_index:]
        with open(self.file_path, "w") as file:
            file.writelines(content)


