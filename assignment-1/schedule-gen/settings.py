from group import Group
from room import Room
from pathlib import Path

class Settings:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def insert_self_studier_group_settings(self, nrof_hosts: int, initial_x: float, initial_y: float, time_tables_dir: Path, route_files_dir: Path, study_room_assignment_file: Path, start_time: int, end_time: int, group_id: int) -> None:
        insertion_lines = []
        has_lecture_takers = group_id > 1 # if no lecture takers, we need to insert Scenario.nrofHostGroups = 1
        if not has_lecture_takers: 
            insertion_lines.append("\nScenario.nrofHostGroups = 1\n")
        insertion_lines.append("\n")
        insertion_lines.append(f"Group{group_id}.groupID = selfstudier_\n")
        insertion_lines.append(f"Group{group_id}.nrofHosts = {nrof_hosts}\n")
        insertion_lines.append(f"Group{group_id}.movementModel = SelfStudierMovement\n")
        insertion_lines.append(f"Group{group_id}.initialX = {initial_x}\n")
        insertion_lines.append(f"Group{group_id}.initialY = {initial_y}\n")
        insertion_lines.append(f"Group{group_id}.timeTablesDir = {time_tables_dir}\n")
        insertion_lines.append(f"Group{group_id}.routeFilesDir = {route_files_dir}\n")
        insertion_lines.append(f"Group{group_id}.studyRoomAssignmentFile = {study_room_assignment_file}\n")
        insertion_lines.append(f"Group{group_id}.routeType = 1\n")
        insertion_lines.append(f"Group{group_id}.routeFirstStop = 0\n")
        insertion_lines.append(f"Group{group_id}.startTime = {start_time}\n")
        insertion_lines.append(f"Group{group_id}.endTime = {end_time}\n")
        insertion_lines.append(f"Group{group_id}.waitTime = 600, 1800\n")
        insertion_lines.append(f"Group{group_id}.router = SprayAndWaitRouter\n")
        insertion_lines.append(f"Group{group_id}.msgTtl = 8\n")
        insertion_lines.append(f"Group{group_id}.speed = 0.5, 1.5\n")
        insertion_lines.append(f"Group{group_id}.nrofInterfaces = 1\n")
        insertion_lines.append(f"Group{group_id}.interface1 = bluetoothInterface\n")
        insertion_lines.append("\n")
        with open(self.file_path, "r") as file:
            content = file.readlines()
            start_index = content.index("## SelfStudier group settings (start)\n") + 1
            end_index = content.index("## SelfStudier group settings (end)\n")
            content = content[:start_index] + insertion_lines + content[end_index:]
        with open(self.file_path, "w") as file:
            file.writelines(content)
    
    def insert_group_settings(self, groups: list[Group], group_data_dir: Path, has_self_studiers = True) -> None:

        insertion_lines = Group.generate_group_settings(groups, group_data_dir, has_self_studiers)

        with open(self.file_path) as file:
            content = file.readlines()
            start_index = content.index("## LectureTaker group settings (start)\n") + 1
            end_index = content.index("## LectureTaker group settings (end)\n")
            content = content[:start_index] + insertion_lines + content[end_index:]
        with open(self.file_path, "w") as file:
            file.writelines(content)

    def insert_room_settings(self, rooms: dict[str, Room], rooms_dir: Path) -> None:

        insertion_lines = Room.generate_room_settings(rooms, rooms_dir)

        with open(self.file_path) as file:
            content = file.readlines()
            start_index = content.index("## Room settings (start)\n") + 1
            end_index = content.index("## Room settings (end)\n")
            content = content[:start_index] + insertion_lines + content[end_index:]
        with open(self.file_path, "w") as file:
            file.writelines(content)

    def get_lecture_takers_initial_coordinates(self) -> tuple[float, float]:
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
        
    def get_world_size(self) -> tuple[int, int]:
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
                
