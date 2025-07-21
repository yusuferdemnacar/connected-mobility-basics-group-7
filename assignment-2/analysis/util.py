from pathlib import Path
import csv

def parse_crowd_estimate(file_path: Path):
    with file_path.open() as f:
        reader = csv.DictReader(f)
        estimates = [row for row in reader]
    return estimates

def parse_timetable(file_path: Path):
    with file_path.open() as f:
        reader = csv.DictReader(f)
        timetable = [row for row in reader]
    return timetable

def is_random(mac_address:str) -> bool:
    if mac_address is None or len(mac_address) != 17:
        return False
    first_octet = int(mac_address.split(":")[0], 16)
    is_random:bool = ((first_octet >> 1) & 0x01) == 0x01
    return is_random

def get_events(captures_dir: Path, day: str, label: str) -> list | None:
    csv_path = captures_dir / f"{day}/{label}.csv"
    events = []
    with open(csv_path, "r") as f:
        next(f)
        for line in f:
            time_str, event_type = line.strip().split(",")
            events.append((time_str, event_type))
    return events

def load_oui_dict(csv_path: Path) -> dict:
    oui_dict = {}
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            oui = row['Assignment'].strip().upper()
            vendor = row['Organization Name'].strip()
            oui_dict[oui] = vendor
    return oui_dict

def eval_oui(mac_address: str, oui_dict: dict) -> str:
    if mac_address is None or len(mac_address) < 8:
        return "Unknown"
    oui = mac_address.replace(":", "").upper()[:6]
    return oui_dict.get(oui, "Unknown")
