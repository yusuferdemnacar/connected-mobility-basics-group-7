from room import Room
from course import Course
from group import Group
from schedule import Schedule
from lecture_slot import LectureSlot
from pathlib import Path
from settings import Settings
import random
import datetime
import matplotlib.pyplot as plt
import json

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "the-one/data"
    input_dir = script_dir.parent / "data"
    settings_file = script_dir.parent / "the-one/assignment-1-settings.txt"
    settings = Settings(settings_file)
    initial_x = 110.0
    initial_y = 110.0
    room_names = [
        "mi-2",
        "mi-3",
        "magistrale",
    ]

    rooms = Room.create_rooms(input_dir, room_names)
    Room.draw_map(rooms, input_dir / "corridor.wkt", output_path=data_dir / "rooms.png", image_width=1000, image_height=1000, scale=10)
    Room.generate_room_settings(rooms)
    main_schedule = Schedule(rooms)
    main_schedule.populate(4)

    main_schedule.visualize()

    courses = [item[1] for item in main_schedule.schedule.items() if item[1] is not None]
    courses_by_time = main_schedule.get_courses_by_time()

    number_of_groups = 5
    nrof_hosts = 3

    groups = []

    max_courses_per_group_schedule = 5 

    def check_time_conflict(slot1_start, slot1_end, slot2_start, slot2_end):
        """
        Checks if two time slots overlap.
        Assumes slot times are datetime.time objects.
        Returns True if they overlap, False otherwise.
        """
        # Overlap condition: (StartA < EndB) and (EndA > StartB)
        return slot1_start < slot2_end and slot1_end > slot2_start

    if not courses:
        print("Warning: No courses available from the main schedule to assign to groups.")

    for i in range(1, number_of_groups + 1):
        group_id = i
        selected_group_courses = []

        if not courses: # If there are no courses at all
            group = Group(group_id, nrof_hosts, [])
            groups.append(group)
            continue

        # Determine the target number of courses for this group
        # It's limited by max_courses_per_group_schedule and the total number of unique courses available
        upper_bound_for_target = min(max_courses_per_group_schedule, len(courses))
        
        num_target_courses = 0
        if upper_bound_for_target > 0:
            # Assign a random number of courses, from 1 up to the determined upper bound
            num_target_courses = random.randint(1, upper_bound_for_target)

        # Create a shuffled list of all available courses to pick from for this group
        candidate_pool = list(courses) # Make a copy
        random.shuffle(candidate_pool)

        for candidate_course in candidate_pool:
            if len(selected_group_courses) >= num_target_courses:
                # Group has reached its target number of non-conflicting courses
                break

            is_conflicting = False
            for existing_course in selected_group_courses:
                if check_time_conflict(
                    candidate_course.lecture_slot.start_time, candidate_course.lecture_slot.end_time,
                    existing_course.lecture_slot.start_time, existing_course.lecture_slot.end_time
                ):
                    is_conflicting = True
                    break
            
            if not is_conflicting:
                selected_group_courses.append(candidate_course)
        
        group = Group(group_id, nrof_hosts, selected_group_courses)
        groups.append(group)

    for group in groups:
        # sort the courses by their time slot
        group.courses.sort(key=lambda x: x.lecture_slot.start_time)
        # fill empty time slots with a special course
        for time_slot in range(8, 18, 2):
            # Check if the time slot is already filled
            if not any(
                course.lecture_slot.start_time.hour == time_slot and course.lecture_slot.end_time.hour == time_slot + 2
                for course in group.courses
            ):
                # If not filled, add a special course
                special_course = Course("Idle", LectureSlot(
                    room=[room for room in rooms if room.name == "magistrale"][0],
                    start_time=datetime.time(hour=time_slot),
                    end_time= datetime.time(hour=time_slot + 2)
                ))
                group.courses.append(special_course)

    for group in groups:
        group.generate_route_file(data_dir / "group-data", initial_x, initial_y)
        group.generate_room_sequence_file(data_dir / "group-data")

    settings.insert_group_settings(groups)
    settings.insert_room_settings(rooms)

    # now fill the empty time slots in each group's course list with a special mg course

    # visualize the course lists for each group with matplotlib
    fig, ax = plt.subplots(figsize=(12, 8)) # Increased figure size for better visibility
    ax.set_title("Course Schedule for Each Group")
    ax.set_xlim(8, 18)  # Assuming courses are scheduled between 8 AM and 6 PM
    ax.set_xlabel("Time Slot (Hour of Day)")
    ax.set_ylabel("Groups")

    group_keys = list(range(1, len(groups) + 1))  # Create a list of group indices (0 to N-1)
    
    # Set y-ticks from 0 to N-1
    ax.set_yticks(range(len(group_keys))) 
    # Set y-tick labels to correspond to the 0 to N-1 positions
    ax.set_yticklabels(group_keys) 
    
    magistrale_color = 'skyblue'
    other_course_color = 'salmon'
    
    # To avoid duplicate labels in the legend
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, color=other_course_color, label='Regular Course'),
        plt.Rectangle((0, 0), 1, 1, color=magistrale_color, label='Idle')
    ]

    # Use enumerate to get a 0-indexed group_idx for plotting
    for group_idx, group in enumerate(groups):
        courses = group.courses
        for course in courses:
            start_time_float = course.lecture_slot.start_time.hour + course.lecture_slot.start_time.minute / 60
            end_time_float = course.lecture_slot.end_time.hour + course.lecture_slot.end_time.minute / 60
            duration = end_time_float - start_time_float
            
            bar_color = magistrale_color if course.id == "Idle" else other_course_color
            
            # Use the numerical group_idx for the y-position of the bar
            ax.barh(group_idx, duration, left=start_time_float, height=0.6, color=bar_color, edgecolor='black')
            
            # Add course ID text in the middle of the bar
            text_x = start_time_float + duration / 2
            # Use the numerical group_idx for the y-position of the text
            text_y = group_idx 
            ax.text(text_x, text_y, course.lecture_slot.room.name if course.lecture_slot.room.name else "N/A", 
                    ha='center', va='center', color='black', fontsize=8)

    ax.legend(handles=legend_elements)
    plt.grid(True, axis='x') # Grid only on x-axis for clarity with bars
    plt.tight_layout()
    plt.show()
    
