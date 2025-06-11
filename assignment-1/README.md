## Assignment 1 Initial Presentation

https://docs.google.com/presentation/d/1Vrsz8ayclsPZGKvpSXSVWiV-8wB-makRSAq_sMJGW-M/edit?slide=id.g35a82b90894_0_46#slide=id.g35a82b90894_0_46

## Simulator

The ONE simulator is used for this assignment.

Homepage: [The ONE Homepage](https://akeranen.github.io/the-one/)

Repository: [The ONE GitHub Repository](https://github.com/akeranen/the-one)

Paper: [The ONE Paper](https://www.netlab.tkk.fi/tutkimus/dtn/theone/pub/the_one_simutools.pdf)

## Setup

1. Install the required python modules with requirements.txt:
    ```
    $ python3 -m pip install -r requirements.txt
    ```

## Running
To run the assignment-1 scenario we have provided, 
1. Run the script (in the assignment-1 directory):
    ```
    bash assignment-1.sh
    ```

The run script will first generate schedules, route files and edit the settings file using the schedule-gen scripts.
It will then run the simulation using default values, if values are not provided. The resulting reports will be produced in the `reports_data` directory.
Run `$ assignment-1.sh --help` to get help information on which command-line arguments are supported. The script will simulate the scenario we have configured, run it for a number of times for statistical importance, and repeat for each message size provided. To generate the plots, we have simulated message sizes ranging from 100 bytes to 5 megabytes, repeating for 50 times each.

Refer to the readme in the schedule-gen directory for more information on what the schedule-gen does.

# Visualizations, plotting, and what's between them

## Data loading
After running the experiments, change into the `the-one` directory: `cd the-one`.
To load the data run the `load_data.py` script, with the same arguments you provided to the previous script, or without any arguments for the default options:
```
    python3 load_data.py --sizes [space-delimited list of message sizes] --runs [number of runs to repeat for each message size]
```

# Plotting
After loading the data, to generate the plots run the `plot.py` script:, with the same arguments you provided to the previous script, or without any arguments for the default options:
```
    python3 plot.py
```
The plots will be outputted to the `figures/` directory.