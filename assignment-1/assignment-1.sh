#!/bin/bash

cd the-one && ./compile.sh
cd -
# Run multiple simulations with different message sizes
for size in 100 1000; do
    sed -e "s/Events1.size = .*/Events1.size = $size/" \
            the-one/assignment-1-settings-communications.txt > "the-one/assignment-1-settings-communications-${size}.txt"
    echo "Running simulations for message size: $size"
    for run in $(seq 1 1); do
        # Create temporary config file with unique scenario name for each run
        sed -e "s/Scenario.name = .*/Scenario.name = CMB_${size}_run${run}/" \
            the-one/assignment-1-settings.txt > "the-one/assignment-1-settings-${size}-${run}.txt"
        
        # Generate schedule per run and message size 
        python3 schedule-gen/main.py \
            --the-one-dir the-one \
            --data-dir the-one/data \
            --map-dir the-one/data/fmi-map \
            --corridor-file-path the-one/data/fmi-map/corridor.wkt \
            --settings-file-path the-one/assignment-1-settings-${size}-${run}.txt \
            --nrof-courses 50 \
            --nrof-lecture-taker-groups 40 \
            --nrof-hosts-per-lecture-taker-group 10 \
            --nrof-self-studier-hosts 100 \

        cd the-one
        echo "  Running simulation $run/1 for size $size"
        
        # Run the simulation
        ./one.sh -b 1 \
            "assignment-1-settings-${size}-${run}.txt" \
            "assignment-1-settings-communications-${size}.txt"
        cd -
    done
    
    echo "Completed all 1 simulations for message size: $size"
    echo ""
done

echo "All simulations completed!"
echo "Check the reports/ directory for generated report files."
