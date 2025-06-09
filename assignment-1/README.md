## Assignment 1 initial presentation

https://docs.google.com/presentation/d/1Vrsz8ayclsPZGKvpSXSVWiV-8wB-makRSAq_sMJGW-M/edit?slide=id.g35a82b90894_0_46#slide=id.g35a82b90894_0_46

## Running
To run the assignment-1 scenario, 
1. Install the required python modules with requirements.txt:
    ```
    pip install -r requirements.txt
    ```
1. Compile the-one (in the-one directory):
    ```
    ./compile.sh
    ```
1. Make the script executable (in the assignment-1 directory):
    ```
    chmod +x assignment-1.sh
    ```
1. Run the script (in the assignment-1 directory):
    ```
    bash assignment-1.sh
    ```

The run script will first generate schedules, route files and edit the settings file using the schedule-gen scripts.
Then it will run the simulation using
The arguments to the subcommands are present in the script. 

Refer to the readme in the schedule-gen directory for more information on what the schedule-gen does.
