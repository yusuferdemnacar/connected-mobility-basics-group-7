from room import Room
from group import Group
from schedule import Schedule
from pathlib import Path
from settings import Settings
from argparse import ArgumentParser
import pickle

if __name__ == "__main__":
    
    parser = ArgumentParser(description="Generate schedule and group data for assignment 1.")
    parser.add_argument("--the-one-dir", type=str, default="the-one", help="Path to the the-one directory. Default is the parent directory of this script.")
    parser.add_argument("--data-dir", type=str, default="the-one/data", help="Path to the data directory of the-one. Default is the-one/data.")
    parser.add_argument("--map-dir", type=str, default="the-one/data/fmi-map", help="Path to the directory containing the room WKT files. Default is the-one/data/fmi-map.")
    parser.add_argument("--corridor-file-path", type=str, default="the-one/data/fmi-map/corridor.wkt", help="Path to the skeleton path WKT file to be used for moving between classrooms. Default is the-one/data/fmi-map/corridor.wkt.")
    parser.add_argument("--settings-file-path", type=str, default="the-one/assignment-1-settings.txt", help="Path to the the-one settings file to be used in the simulation. Default is the-one/assignment-1-settings.txt.")
    # TODO: Check this value
    parser.add_argument("--nrof-courses", type=int, default=5, help="Number of courses to be generated. Cannot be larger than the number of rooms * 5. Default is 5.")
    parser.add_argument("--nrof-lt-groups", type=int, default=5, help="Number of lecture taker groups to be generated. Default is 5.")
    parser.add_argument("--nrof-hosts-per-lt-group", type=int, default=3, help="Number of students per lecture taker group. Default is 3.")

    args = parser.parse_args()

    the_one_dir = Path(args.the_one_dir)
    data_dir = Path(args.data_dir)
    map_dir = Path(args.map_dir)
    corridor_file = Path(args.corridor_file_path)
    settings_file = Path(args.settings_file_path)
    nrof_courses = args.nrof_courses
    number_of_lt_groups = args.nrof_lt_groups
    nrof_hosts_per_lt_group = args.nrof_hosts_per_lt_group

    # TODO: Handle missing directories

    settings = Settings(settings_file)
    initial_x, initial_y = settings.get_lecture_takers_initial_coordinates()
    world_size_x, world_size_y = settings.get_world_size()
    
    room_names = Room.get_room_names(map_dir, corridor_file.stem)

    rooms = Room.create_rooms(map_dir, room_names)
    Room.draw_map(rooms, corridor_file, output_path=data_dir / "rooms.png", image_width=world_size_x, image_height=world_size_y, scale=10)
    main_schedule = Schedule(rooms)
    main_schedule.populate(nrof_courses)

    groups = []

    for i in range(1, number_of_lt_groups + 1):
        group_id = i
        group = Group(group_id, nrof_hosts_per_lt_group, main_schedule.generate_random_enrollment())
        groups.append(group)
        group.fill_with_idle_period(rooms["magistrale"])

    for group in groups:
        group.generate_route_file(data_dir / "group-data", initial_x, initial_y)
        group.generate_schedule_file(data_dir / "group-data")
    
    settings.insert_group_settings(groups, data_dir.relative_to(the_one_dir) / "group-data")
    settings.insert_room_settings(rooms, map_dir.relative_to(the_one_dir))
    
    with open("schedule-gen/main_schedule.pkl", "wb") as f:
        pickle.dump(main_schedule, f)

    with open("schedule-gen/groups.pkl", "wb") as f:
        pickle.dump(groups, f)
