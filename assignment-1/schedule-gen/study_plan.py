from datetime import time, timedelta, datetime
import random
from time_interval import TimeInterval
from room import Room
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class StudyPlan:
    def __init__(self, start_time: time = time(8, 0), duration: timedelta = timedelta(hours=12), room: str = "library", intervals: list[TimeInterval] = None) -> None:
        self.start_time = start_time
        self.end_time = (datetime.combine(datetime.min.date(), start_time) + duration).time()
        self.duration = duration
        self.room = room
        self.intervals = intervals

    @staticmethod
    def generate_study_room_assignment_file(study_plans: list['StudyPlan'], file_path: str) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as file:
            for i, study_plan in enumerate(study_plans):
                file.write(f"{i + 1}, {study_plan.room.name}\n")

    def generate_route_file(self, file_path: str, initial_x: float, initial_y: float) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as file:
            file.write("LINESTRING (")
            for interval in self.intervals:
                if interval.type == "study":
                    file.write(f"{self.room.door_inside_x} {self.room.door_inside_y}, ")
                elif interval.type == "break":
                    file.write(f"{self.room.door_outside_x} {self.room.door_outside_y}, ")
            file.write(f"{initial_x} {initial_y})\n")
    
    def generate_timetable_file(self, file_path: str) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as file:
            # each line holds an integer corresponding to simulator time (seconds)
            # the start and end times are from 8 am so we subtract 8 hours
            first_end_time = self.intervals[0].end_time.hour * 3600 + self.intervals[0].end_time.minute * 60
            first_end_time -= 8 * 3600
            file.write(f"{first_end_time}\n")
            for interval in self.intervals[1:]:
                end_time = interval.end_time.hour * 3600 + interval.end_time.minute * 60
                end_time -= 8 * 3600
                file.write(f"{end_time}\n")

    @staticmethod
    def random_study_plan(rooms: list[Room]) -> 'StudyPlan':
        room = random.choice(rooms)
        intervals = []
        nrof_sessions = random.randint(1, 5)
        first_session_duration = random.randint(30, 90)
        intervals.append(TimeInterval(time(8, 0), timedelta(minutes=first_session_duration), "study"))
        for _ in range(nrof_sessions - 1):
            break_duration = random.randint(5, 20)
            intervals.append(TimeInterval(intervals[-1].end_time, timedelta(minutes=break_duration), "break"))
            session_duration = random.randint(30, 90)
            intervals.append(TimeInterval(intervals[-1].end_time, timedelta(minutes=session_duration), "study"))
        
        total_duration = sum((interval.duration for interval in intervals), start=timedelta())
        offset_minutes = random.randint(0, (int) ((timedelta(hours=12) - total_duration).total_seconds()) // 60)
        
        # Offset start and end times of intervals with the random offset
        for interval in intervals:
            interval.start_time = (datetime.combine(datetime.min.date(), interval.start_time) + timedelta(minutes=offset_minutes)).time()
            interval.end_time = (datetime.combine(datetime.min.date(), interval.end_time) + timedelta(minutes=offset_minutes)).time()

        return StudyPlan(intervals[0].start_time, total_duration, room, intervals)

    # GitHub Copilot was utilized to implement the visualization. 
    # It is not an essential part of the implementation, it is just for debugging purposes.

    @staticmethod
    def visualize(study_plans: list['StudyPlan']) -> None:
        if not study_plans:
            print("No study plans provided to visualize.")
            return

        fig, ax = plt.subplots(figsize=(15, 2 + len(study_plans) * 0.8)) # Adjust height based on number of plans
        ax.set_title("Study Plans Overview")
        ax.set_xlabel("Time of Day")
        ax.set_ylabel("Study Plan / Room")

        # Use a dummy date for converting time objects to datetime for plotting
        dummy_date = datetime.min.date()

        # Colors for different interval types
        study_color = 'lightcoral'
        break_color = 'lightskyblue'

        plan_labels = []
        all_start_times = []
        all_end_times = []

        for y_pos, study_plan_instance in enumerate(study_plans):
            plan_labels.append(f"Plan {y_pos+1} ({study_plan_instance.room})")
            if not study_plan_instance.intervals:
                print(f"Study plan for {study_plan_instance.room} has no intervals.")
                continue

            all_start_times.append(study_plan_instance.intervals[0].start_time)
            all_end_times.append(study_plan_instance.intervals[-1].end_time)

            for interval in study_plan_instance.intervals:
                # Convert start_time and end_time to datetime objects for plotting
                start_datetime = datetime.combine(dummy_date, interval.start_time)
                end_datetime = datetime.combine(dummy_date, interval.end_time)
                
                # Calculate duration for bar width (matplotlib uses floats for datetime)
                start_num = mdates.date2num(start_datetime)
                end_num = mdates.date2num(end_datetime)
                duration_num = end_num - start_num

                bar_color = study_color if interval.type == "study" else break_color # Assuming type exists
                
                ax.barh(y_pos, duration_num, left=start_num, height=0.6, color=bar_color, edgecolor='black')
                
                # Add text label for the interval
                text_x_datetime = start_datetime + (interval.duration / 2)
                text_x_num = mdates.date2num(text_x_datetime)
                
                ax.text(text_x_num, y_pos, f"{interval.type}\n({interval.duration.total_seconds() // 60:.0f}m)",
                        ha='center', va='center', color='black', fontsize=8)

        # Format the x-axis to show time
        ax.xaxis_date() 
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # Set x-axis limits based on the overall earliest start and latest end
        if all_start_times and all_end_times:
            min_start_time = min(all_start_times)
            max_end_time = max(all_end_times)
            
            plot_start_dt = datetime.combine(dummy_date, min_start_time) - timedelta(minutes=30)
            plot_end_dt = datetime.combine(dummy_date, max_end_time) + timedelta(minutes=30)
            ax.set_xlim(plot_start_dt, plot_end_dt)
        else: # Fallback if no intervals were plotted
            ax.set_xlim(datetime.combine(dummy_date, time(7,0)), datetime.combine(dummy_date, time(21,0)))


        ax.set_yticks(range(len(study_plans))) 
        ax.set_yticklabels(plan_labels) 
        ax.invert_yaxis() # To have the first plan at the top

        # Create legend
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, color=study_color, label='Study Session'),
            plt.Rectangle((0, 0), 1, 1, color=break_color, label='Break')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1.05 + 0.05 * (len(study_plans)/5) ))


        plt.grid(True, axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

# Example Usage:
if __name__ == "__main__":
    pass