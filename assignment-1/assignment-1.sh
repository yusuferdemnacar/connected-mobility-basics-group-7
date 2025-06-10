python3 schedule-gen/main.py \
    --the-one-dir the-one \
    --data-dir the-one/data \
    --map-dir the-one/data/fmi-map \
    --corridor-file-path the-one/data/fmi-map/corridor.wkt \
    --settings-file-path the-one/assignment-1-settings.txt \
    --nrof-courses 5 \
    --nrof-lecture-taker-groups 5 \
    --nrof-hosts-per-lecture-taker-group 3 \
    --nrof-self-studier-hosts 5 \

cd the-one

./compile.sh

# Run multiple simulations with different message sizes
for size in 100 1000 10000 100000 1000000 5000000; do
    echo "Running simulations for message size: $size"
    
    # Run multiple simulations for each message size
    for run in $(seq 1 100); do
        echo "  Running simulation $run/1 for size $size"
        
        # Create temporary config file with unique scenario name for each run
        sed -e "s/Scenario.name = .*/Scenario.name = CMB_${size}_run${run}/" \
            assignment-1-settings.txt > "assignment-1-settings-${size}.txt"
        sed -e "s/Events1.size = .*/Events1.size = $size/" \
            assignment-1-settings-communications.txt > "assignment-1-settings-communications-${size}.txt"
        
        # Run the simulation
        ./one.sh -b 1 \
            "./assignment-1-settings-${size}.txt" \
            "./assignment-1-settings-communications-${size}.txt"
    done
    
    echo "Completed all 1 simulations for message size: $size"
    echo ""
done

echo "All simulations completed!"
echo "Check the reports/ directory for generated report files."
