from group import Group
from room import Room
from pathlib import Path

class Settings:
    def __init__(self, file_path: Path):
        self.file_path = file_path
    
    def insert_group_settings(self, groups) -> None:

        insertion_lines = Group.generate_group_settings(groups)

        with open(self.file_path) as file:
            content = file.readlines()
            start_index = content.index("## Group settings (start)\n") + 1
            end_index = content.index("## Group settings (end)\n")
            content = content[:start_index] + insertion_lines + content[end_index:]
        with open(self.file_path, "w") as file:
            file.writelines(content)

    def insert_room_settings(self, rooms) -> None:

        insertion_lines = Room.generate_room_settings(rooms)

        with open(self.file_path) as file:
            content = file.readlines()
            start_index = content.index("## Room settings (start)\n") + 1
            end_index = content.index("## Room settings (end)\n")
            content = content[:start_index] + insertion_lines + content[end_index:]
        with open(self.file_path, "w") as file:
            file.writelines(content)

    def get_lecture_takers_initial_coordinates(self) -> tuple:
        initial_x, initial_y = 0.0, 0.0
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if line.startswith("LectureTakerMovement.initialX = "):
                        initial_x = float(line.split('=')[1].strip())
                    elif line.startswith("LectureTakerMovement.initialY = "):
                        initial_y = float(line.split('=')[1].strip())
            return initial_x, initial_y
        except FileNotFoundError:
            print(f"File {self.file_path} not found. Please check the path.")
            return 0, 0
        
    def get_world_size(self) -> tuple:
        world_size_x, world_size_y = 0.0, 0.0
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if line.startswith("MovementModel.worldSize = "):
                        world_size_x, world_size_y = map(int, line.split('=')[1].strip().split(','))
            return world_size_x, world_size_y
        except FileNotFoundError:
            print(f"File {self.file_path} not found. Please check the path.")
            return 0, 0
                
