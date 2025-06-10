from group import Group
from study_plan import StudyPlan
from pathlib import Path
import argparse
import pickle

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Visualize the main schedule and group schedules.")
    parser.add_argument("--main-schedule", type=str, help="Path to the main schedule pickle file.", default="main_schedule.pkl")
    parser.add_argument("--groups", type=str, help="Path to the groups pickle file.", default="groups.pkl")
    parser.add_argument("--study-plans", type=str, help="Path to the self-studiers' study plans pickle file.", default="study_plans.pkl")

    args = parser.parse_args()

    main_schedule_path = Path(args.main_schedule)
    with open(main_schedule_path, 'rb') as file:
        main_schedule = pickle.load(file)

    groups_path = Path(args.groups)
    with open(groups_path, 'rb') as file:
        groups = pickle.load(file)

    study_plans_path = Path(args.study_plans)
    with open(study_plans_path, 'rb') as file:
        study_plans = pickle.load(file)
    
    main_schedule.visualize()
    Group.visualize(groups)
    StudyPlan.visualize(study_plans)
