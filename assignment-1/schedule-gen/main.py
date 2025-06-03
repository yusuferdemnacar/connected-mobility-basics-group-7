from room import Room
from group import Group
from schedule import Schedule
from pathlib import Path
from settings import Settings

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "the-one/data"
    map_dir = data_dir / "fmi-map"
    corridor_file = map_dir / "corridor.wkt"
    settings_file = script_dir.parent / "the-one/assignment-1-settings.txt"
    settings = Settings(settings_file)
    initial_x, initial_y = settings.get_lecture_takers_initial_coordinates()
    
    room_names = Room.get_room_names(map_dir)

    rooms = Room.create_rooms(map_dir, room_names)
    Room.draw_map(rooms, corridor_file, output_path=data_dir / "rooms.png", image_width=1000, image_height=1000, scale=10)
    main_schedule = Schedule(rooms)
    main_schedule.populate(2)

    number_of_groups = 5
    nrof_hosts = 3

    groups = []

    for i in range(1, number_of_groups + 1):
        group_id = i
        group = Group(group_id, nrof_hosts, main_schedule.generate_random_enrollment())
        groups.append(group)
        group.fill_with_idle_period(rooms["magistrale"])

    for group in groups:
        group.generate_route_file(data_dir / "group-data", initial_x, initial_y)
        group.generate_room_sequence_file(data_dir / "group-data")

    settings.insert_group_settings(groups)
    settings.insert_room_settings(rooms)

    # main_schedule.visualize()
    # Group.visualize(groups)
