from group import Group
from pathlib import Path
import argparse
import pickle

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Visualize the main schedule and group schedules.")
    parser.add_argument("--main-schedule", type=str, help="Path to the main schedule pickle file.")
    parser.add_argument("--groups", type=str, help="Path to the groups pickle file.")

    args = parser.parse_args()
    
    if not args.main_schedule and not args.groups:
        print("At least one of --main-schedule or --groups must be provided.")
        exit(1)

    if args.main_schedule:
        main_schedule_path = Path(args.main_schedule)
        with open(main_schedule_path, 'rb') as file:
            main_schedule = pickle.load(file)
        
        main_schedule.visualize()

    if args.groups:
        groups_path = Path(args.groups)
        with open(groups_path, 'rb') as file:
            groups = pickle.load(file)
        
        Group.visualize(groups)
