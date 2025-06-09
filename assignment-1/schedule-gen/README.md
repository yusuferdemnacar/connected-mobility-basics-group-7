# Schedule Generation
## Requirements
- Pillow
- matplotlib

The requirements file is located in the assignment-1 directory.

## Lecture Takers

1. Generate an overall course schedule with the specified number of courses.

2. Generate a specified number of groups and generates a conflict-free schedule with at least one course in it for each group.

3. Generate the necessary the-one settings of the groups and inserts them into the settings file.

4. Generate the required (by the-one) route and schedule files for each group.

5. Save the generated schedule and the groups for later visualization.

6. Draw the background map image of the scenario.
### Usage
See the help messages for each script for more details.
```
python main.py --help
```
### Visualization
Visualize the generated overall schedule and the groups' schedules after running the main script.
```
python visualize.py --help
```