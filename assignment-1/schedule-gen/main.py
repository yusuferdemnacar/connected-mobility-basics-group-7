from room import Room
from group import Group
from schedule import Schedule
from study_plan import StudyPlan
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
    parser.add_argument("--nrof-lecture-taker-groups", type=int, default=5, help="Number of lecture taker groups to be generated. Default is 5.")
    parser.add_argument("--nrof-hosts-per-lecture-taker-group", type=int, default=3, help="Number of students per lecture taker group. Default is 3.")
    parser.add_argument("--nrof-self-studier-hosts", type=int, default=5, help="Number of self-studier hosts to be generated. Default is 5.")

    args = parser.parse_args()

    the_one_dir = Path(args.the_one_dir)
    data_dir = Path(args.data_dir)
    map_dir = Path(args.map_dir)
    corridor_file = Path(args.corridor_file_path)
    settings_file = Path(args.settings_file_path)
    nrof_courses = args.nrof_courses
    nrof_lecture_taker_groups = args.nrof_lecture_taker_groups
    nrof_hosts_per_lecture_taker_group = args.nrof_hosts_per_lecture_taker_group
    nrof_self_studier_hosts = args.nrof_self_studier_hosts

    # TODO: Handle missing directories

    settings = Settings(settings_file)
    initial_x, initial_y = settings.get_lecture_takers_initial_coordinates()
    world_size_x, world_size_y = settings.get_world_size()
    
    room_names = Room.get_room_names(map_dir, corridor_file.stem)

    rooms = Room.create_rooms(map_dir, room_names)
    # Room.draw_map(rooms, corridor_file, output_path=data_dir / "rooms.png", image_width=world_size_x, image_height=world_size_y, scale=10)
    main_schedule = Schedule(rooms)
    main_schedule.populate(nrof_courses)

    groups = []

    for i in range(1, nrof_lecture_taker_groups + 1):
        group_id = i
        group = Group(group_id, nrof_hosts_per_lecture_taker_group, main_schedule.generate_random_enrollment())
        groups.append(group)
        group.fill_with_idle_period(rooms["magistrale"])

    for group in groups:
        group.generate_route_file(data_dir / "group-data", initial_x, initial_y)
        group.generate_schedule_file(data_dir / "group-data")

    self_study_rooms = [room for room in rooms.values() if room.name == "library" or room.name == "computerhall"]

    study_plans = [StudyPlan.random_study_plan(self_study_rooms) for _ in range(nrof_self_studier_hosts)]
    self_study_start_time = min(study_plan.start_time for study_plan in study_plans)
    self_study_end_time = max(study_plan.end_time for study_plan in study_plans)

    self_study_start_time_seconds = self_study_start_time.hour * 3600 + self_study_start_time.minute * 60 - 8 * 3600
    self_study_end_time_seconds = self_study_end_time.hour * 3600 + self_study_end_time.minute * 60 - 8 * 3600

    for i, study_plan in enumerate(study_plans):
        study_plan.generate_route_file(data_dir / "group-data" / "self-studier" / "routes" / f"self_studier_{i + 1}_route.wkt", initial_x, initial_y)
        study_plan.generate_timetable_file(data_dir / "group-data" / "self-studier" / "time-tables" / f"self_studier_{i + 1}_timetable.txt")

    StudyPlan.generate_study_room_assignment_file(study_plans, data_dir / "group-data" / "self-studier" / "study-room-assignment.txt")
    
    settings.insert_group_settings(groups, data_dir.relative_to(the_one_dir) / "group-data")
    settings.insert_room_settings(rooms, map_dir.relative_to(the_one_dir))
    self_studier_time_tables_dir = data_dir / "group-data" / "self-studier" / "time-tables"
    self_studier_routes_dir = data_dir / "group-data" / "self-studier" / "routes"
    self_studier_study_room_assignment_file = data_dir / "group-data" / "self-studier" / "study-room-assignment.txt"
    settings.insert_self_studier_group_settings(nrof_self_studier_hosts, initial_x, initial_y, self_studier_time_tables_dir.relative_to(the_one_dir), self_studier_routes_dir.relative_to(the_one_dir), self_studier_study_room_assignment_file.relative_to(the_one_dir), self_study_start_time_seconds, self_study_end_time_seconds, nrof_lecture_taker_groups + 1)

    with open("schedule-gen/main_schedule.pkl", "wb") as f:
        pickle.dump(main_schedule, f)

    with open("schedule-gen/groups.pkl", "wb") as f:
        pickle.dump(groups, f)

    with open("schedule-gen/study_plans.pkl", "wb") as f:
        pickle.dump(study_plans, f)
