from pathlib import Path

class Group:
    def __init__(self, id: int, nrof_hosts: int = 1, courses: list = None):
        self.id = id
        self.nrof_hosts = nrof_hosts
        self.courses = courses

    def generate_route_file(self, file_path: Path, initial_x: float, initial_y: float):
        file_path.mkdir(parents=True, exist_ok=True)
        with open(file_path / f"group{self.id}_route.wkt", "w") as file:
            file.write("LINESTRING (")
            self.courses.sort(key=lambda x: x.lecture_slot.start_time)
            for course in self.courses:
                file.write(f"{course.lecture_slot.room.door_inside_x} {course.lecture_slot.room.door_inside_y}, ")
            file.write(f"{initial_x} {initial_y})\n")

    def generate_room_sequence_file(self, file_path: Path):
        self.courses.sort(key=lambda x: x.lecture_slot.start_time)
        file_path.mkdir(parents=True, exist_ok=True)
        with open(file_path / f"group{self.id}_room_sequence.txt", "w") as file:
            for course in self.courses:
                file.write(f"{course.lecture_slot.room.name}\n")

    # TODO: make all settings configurable
    @staticmethod
    def generate_group_settings(groups: list) -> list:
        lines = []
        lines.append(f"Scenario.nrofHostGroups = {len(groups)}\n")
        for group in groups:
            lines.append(f"# Group{group.id} settings\n")
            lines.append(f"Group{group.id}.groupID = group{group.id}\n")
            lines.append(f"Group{group.id}.nrofHosts = {group.nrof_hosts}\n")
            lines.append(f"Group{group.id}.movementModel = LectureTakerMovement\n")
            lines.append(f"Group{group.id}.routeFile = data/group-data/group{group.id}_route.wkt\n")
            lines.append(f"Group{group.id}.routeType = 1\n")
            lines.append(f"Group{group.id}.routeFirstStop = 0\n")
            lines.append(f"Group{group.id}.router = EpidemicRouter\n")
            lines.append(f"Group{group.id}.bufferSize = 5M\n")
            lines.append(f"Group{group.id}.speed = 0.5, 1.5\n")
            lines.append(f"Group{group.id}.nrofInterfaces = 1\n")
            lines.append(f"Group{group.id}.interface1 = btInterface\n")
            lines.append(f"Group{group.id}.msgTtl = 300\n")
        return lines