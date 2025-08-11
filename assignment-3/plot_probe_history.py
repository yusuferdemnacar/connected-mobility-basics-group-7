import requests
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime, timedelta, timezone
from collections import defaultdict

def fetch_asn_history_daily(probe_ids, date_gte=None, date_lte=None):
    
    fetch_gte = (date_gte - timedelta(days=2)) if date_gte else None
    fetch_lte = (date_lte + timedelta(days=2)) if date_lte else None
    
    gte_str = fetch_gte.strftime('%Y-%m-%d') if fetch_gte else None
    lte_str = fetch_lte.strftime('%Y-%m-%d') if fetch_lte else None
    
    url = "https://atlas.ripe.net/api/v2/probes/archive/"
    params = {
        "probe": probe_ids,
        "format": "json"
    }
    if gte_str:
        params["date__gte"] = gte_str
    if lte_str:
        params["date__lte"] = lte_str

    results = []
    page = 1
    while url:
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            sys.exit(1)
            
        data = resp.json()
        results.extend(data.get("results", []))
        url = data.get("next")
        params = {}
        page += 1
    return results

def plot_daily_asn_history(data, view_start_date, view_end_date):
    if not data:
        print("No data to plot.")
        return

    probes_data = defaultdict(list)
    for entry in data:
        probes_data[entry['id']].append(entry)

    probe_ids = sorted(probes_data.keys())
    num_probes = len(probe_ids)
    
    highlight_ids = set([
        1006477, 1006896, 1006948, 1007159, 1007645, 1008228, 1008786, 1009988, 1010332, 1011217,
        13040, 28430, 50524, 51136, 60323, 62613, 63017, 63025, 64237, 1010769
    ])

    fig, ax = plt.subplots(figsize=(15, 8))
    y_pos = range(num_probes)

    for i, probe_id in enumerate(probe_ids):
        entries = sorted(probes_data[probe_id], key=lambda x: x['date'])
        for j, entry in enumerate(entries):
            start_date = datetime.fromtimestamp(entry['status_since'], tz=timezone.utc)
            if j + 1 < len(entries):
                end_date = datetime.fromtimestamp(entries[j+1]['status_since'], tz=timezone.utc)
            else:
                day_of_entry = datetime.strptime(entry['date'], "%Y%m%d").replace(tzinfo=timezone.utc)
                end_date = day_of_entry + timedelta(days=1)
            if start_date >= end_date:
                continue
            plot_start = max(start_date, view_start_date)
            plot_end = min(end_date, view_end_date)
            if plot_start >= plot_end:
                continue
            asn = entry.get("asn_v4")
            status = entry.get("status", {}).get("name", "")
            
            is_starlink = asn in [14593, 45700]
            is_highlighted = probe_id in highlight_ids

            if is_starlink:
                if is_highlighted:
                    color = 'tab:blue'
                else:
                    color = 'lightblue'
            else:
                color = 'tab:orange'

            if status.lower() not in ["connected", "online"]:
                color = "tab:red"
            ax.barh(
                y=i,
                width=(plot_end - plot_start),
                left=plot_start,
                height=0.5,
                color=color,
                edgecolor="black",
                linewidth=0.5
            )
    yticklabels = []
    for pid in probe_ids:
        if int(pid) in highlight_ids:
            yticklabels.append(f"$\\bf{{{pid}}}$")
        else:
            yticklabels.append(str(pid))
    ax.set_yticks(y_pos)
    ax.set_yticklabels(yticklabels)
    ax.invert_yaxis()

    ax.set_xlabel("Date-Time")
    ax.set_ylabel("Probe ID")
    ax.set_title(f"Daily ASN History of RIPE Atlas Probes from {view_start_date} to {view_end_date}")

    ax.set_xlim(view_start_date, view_end_date)
    
    locator = mdates.AutoDateLocator()
    auto_ticks = locator.tick_values(view_start_date, view_end_date)
    all_ticks = sorted(list(set(list(auto_ticks) + [mdates.date2num(view_start_date), mdates.date2num(view_end_date)])))
    
    ax.xaxis.set_major_locator(mticker.FixedLocator(all_ticks))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()

    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, color='tab:blue', label='Starlink (ASN 14593, 45700) - Used'),
        plt.Rectangle((0, 0), 1, 1, color='lightblue', label='Starlink (ASN 14593, 45700) - Unused'),
        plt.Rectangle((0, 0), 1, 1, color='tab:orange', label='Other ASN'),
        plt.Rectangle((0, 0), 1, 1, color='tab:red', label='Offline/Disconnected')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig(f"report/images/analysis/asn_history_{view_start_date.strftime('%Y%m%d')}_{view_end_date.strftime('%Y%m%d')}.png")
    plt.show()

def parse_datetime(dt_str):
    try:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.strptime(dt_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plot_probe_history.py PROBE_ID1 [PROBE_ID2...] [YYYY-MM-DD HH:MM:SS] [YYYY-MM-DD HH:MM:SS]")
        print("Example: python plot_probe_history.py 1011217 \"2025-07-26 12:00:00\" \"2025-08-02 12:00:00\"")
        print("Note: You may not need to quote datetime arguments depending on your shell.")
        sys.exit(1)

    args = sys.argv[1:]
    probe_ids = []
    datetime_strings = []
    
    i = 0
    while i < len(args):
        arg = args[i]
        try:
            int(arg)
            probe_ids.append(arg)
            i += 1
            continue
        except ValueError:
            pass

        if '-' in arg and len(arg.split('-')) == 3:
            if i + 1 < len(args) and ':' in args[i+1] and len(args[i+1].split(':')) == 3:
                datetime_strings.append(f"{arg} {args[i+1]}")
                i += 2
            else:
                datetime_strings.append(arg)
                i += 1
        else:
            print(f"Warning: Ignoring unrecognized argument '{arg}'")
            i += 1

    if not probe_ids:
        print("Error: No probe IDs provided.")
        sys.exit(1)

    view_end_date = datetime.now(timezone.utc)
    view_start_date = view_end_date - timedelta(days=7)

    if len(datetime_strings) >= 1:
        view_start_date = parse_datetime(datetime_strings[0])
    if len(datetime_strings) >= 2:
        view_end_date = parse_datetime(datetime_strings[1])

    if view_start_date >= view_end_date:
        print("Error: Start date must be before end date.")
        sys.exit(1)

    probe_ids_arg = ",".join(probe_ids)
    
    history_data = fetch_asn_history_daily(probe_ids_arg, view_start_date, view_end_date)
    
    plot_daily_asn_history(history_data, view_start_date, view_end_date)

    print(f"Total probes: {len(probe_ids)}")