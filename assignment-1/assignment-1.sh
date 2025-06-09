python schedule-gen/main.py \
    --the-one-dir the-one \
    --data-dir the-one/data \
    --map-dir the-one/data/fmi-map \
    --corridor-file-path the-one/data/fmi-map/corridor.wkt \
    --settings-file-path the-one/assignment-1-settings.txt \
    --nrof-courses 5 \
    --nrof-lt-groups 5 \
    --nrof-hosts-per-lt-group 3

cd the-one

./compile.sh

# list the settings file here
./one.sh \
    ./assignment-1-settings.txt \
    ./assignment-1-settings-communications.txt \
