import pathlib
import os
import argparse
import csv

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Generate map files of FMI from QGIS exports.")
    parser.add_argument("--corridor_raw", type=str, required=False, default="map-gen/data/corridor_raw.csv", help="Path to the unaltered corridor csv export containing corridor lines.")
    parser.add_argument("--rooms_aggregate", type=str, required=False, default="map-gen/data/rooms_aggregate.csv", help="Path to the csv export containing corner points of rooms with room names.")
    parser.add_argument("--doors_aggregate", type=str, required=False, default="map-gen/data/doors_aggregate.csv", help="Path to the csv export containing inside and outside door points with room names.")
    parser.add_argument("--output_dir", type=str, required=False, default="the-one/data/fmi-map", help="Directory to save the generated room and corridor files.")

    args = parser.parse_args()
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    corridor_raw_path = pathlib.Path(args.corridor_raw)
    rooms_aggregate_path = pathlib.Path(args.rooms_aggregate)
    doors_aggregate_path = pathlib.Path(args.doors_aggregate)

    if rooms_aggregate_path.exists() and doors_aggregate_path.exists():
        rooms = {}
        with open(rooms_aggregate_path, 'r') as rooms_file, open(doors_aggregate_path, 'r') as doors_file:
            rooms_reader = csv.DictReader(rooms_file)
            doors_reader = csv.DictReader(doors_file)
            for row in doors_reader:
                row['name'] = row['name'].replace(".", "_")
                if row['name'] not in rooms:
                    rooms[row['name']] = []
                rooms[row['name']].append(row['WKT'])
            for row in rooms_reader:
                row['name'] = row['name'].replace(".", "_")
                if row['name'] not in rooms:
                    rooms[row['name']] = []
                rooms[row['name']].append(row['WKT'])
        for room_name, wkt_lines in rooms.items():
            with open(output_dir / f"{room_name}.wkt", 'w') as room_file:
                for line in wkt_lines:
                    room_file.write(line + '\n')
        print(f"Rooms written to {output_dir}.")
    else:
        print(f"Rooms aggregate file {rooms_aggregate_path} or doors aggregate file {doors_aggregate_path} does not exist.")

    if corridor_raw_path.exists():
        with open(corridor_raw_path, 'r') as corridor_file:
            corridor_lines = corridor_file.readlines()
        with open(output_dir / "corridor.wkt", 'w') as corridor_file:
            for line in corridor_lines[1:]:
                corridor_file.write(line.strip().strip("\"") + '\n')
        print(f"Corridor written to {output_dir}.")
    else:
        print(f"Corridor raw file {corridor_raw_path} does not exist.")
                
