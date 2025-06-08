from pathlib import Path
from PIL import Image, ImageDraw

class Room:
    def __init__(self, name: str, points: list[tuple[float, float]], door_inside_x: float, door_inside_y: float, door_outside_x: float, door_outside_y: float) -> None:
        self.name = name
        self.points = points
        self.door_inside_x, self.door_inside_y = door_inside_x, door_inside_y
        self.door_outside_x, self.door_outside_y = door_outside_x, door_outside_y

    def __repr__(self):        
        return f"Room({self.name}, Points: ({self.points}))"
    
    @staticmethod
    def get_room_names(file_path: Path, corridor_file_name: str) -> list[str]:
        try:
            room_names = [file.stem for file in file_path.glob("*.wkt")]
            if not room_names:
                print(f"No room files found in {file_path}.")
            return [name for name in room_names if name != corridor_file_name]
        except Exception as e:
            print(f"Error reading room names from {file_path}: {e}")
            return
    
    @staticmethod
    def create_rooms(file_path: Path, room_names: list) -> dict[str, 'Room']:
        rooms = {}
        for room_name in room_names:
            try:
                with open(file_path / f"{room_name}.wkt", 'r') as file:
                    points = []
                    reader = file.readlines()
                    outside_door_x, outside_door_y = map(float, reader[0].lstrip("POINT (").rstrip(")\n").split(" "))
                    inside_door_x, inside_door_y = map(float, reader[1].lstrip("POINT (").rstrip(")\n").split(" "))
                    for line in reader[2:]:
                        line = line.lstrip("POINT (").rstrip(")\n")
                        x, y = map(float, line.split(" "))
                        points.append((x, y))
                    if len(points) < 3:
                        ValueError(f"Room {room_name} has less than 3 points.")
                    room = Room(room_name, points, inside_door_x, inside_door_y, outside_door_x, outside_door_y)
                    rooms[room_name] = room
            except FileNotFoundError:
                print(f"File {file_path} not found.")
                return []
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return []
        return rooms
    
    @staticmethod
    def generate_room_settings(rooms: dict[str, 'Room'], rooms_dir: Path) -> list[str]:
        lines = []
        lines.append("\n")
        for room in rooms.values():
            lines.append(f"LectureTakerMovement.{room.name}.file = {rooms_dir}/{room.name}.wkt\n")
        lines.append("\n")
        return lines
    
    @staticmethod
    def draw_map(rooms, corridor_file, output_path="rooms.png", image_width=1000, image_height=1000, scale=1, wall_color="black", room_color="lightgray", corridor_color="red", line_width=0.5, background_color="white") -> None:

        img = Image.new("RGB", (image_width * scale, image_height * scale), background_color)
        draw = ImageDraw.Draw(img)

        for room in rooms.values():
            draw.polygon(
                [(x * scale, y * scale) for x, y in room.points],
                outline = wall_color,
                fill = room_color,
                width = int(line_width * scale)
            )

        with open(corridor_file, 'r') as file:
            for line in file:
                line = line.lstrip("LINESTRING (").rstrip(")\n")
                line = line.lstrip("MULTILINESTRING ((").rstrip("))\n")
                points = [tuple(map(float, point.split())) for point in line.split(",")]

                draw.line(
                    [(x * scale, y * scale) for x, y in points],
                    fill = corridor_color,
                    width = int(line_width * scale)
                )
            
        try:
            img.save(output_path)
            print(f"Image saved to {output_path}")
        except Exception as e:
            print(f"Error saving image to {output_path}: {e}")

if __name__ == "__main__":
    pass