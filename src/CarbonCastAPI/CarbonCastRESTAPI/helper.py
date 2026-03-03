import csv
import os
from datetime import datetime, timezone


class RealTimeDataNotFoundError(Exception):
    """Raised when real_time data directory or expected CSV files are missing."""
    def __init__(self, region_code, path, message=None):
        self.region_code = region_code
        self.path = path
        self.message = message or (
            f"No data for region '{region_code}'. Looked in: {path}. "
            "Ensure real_time/<region>/ exists with files like "
            "<region>_<date>_lifecycle_emissions.csv and <region>_<date>_direct_emissions.csv"
        )
        super().__init__(self.message)


def get_latest_csv_file(region_code):
    path = os.path.abspath(os.path.join(os.getcwd(), 'real_time', region_code))
    if not os.path.isdir(path):
        raise RealTimeDataNotFoundError(region_code, path, message=(
            f"Directory not found: {path}. Run the server from CarbonCastAPI and create "
            "real_time/<region>/ with CSV files, or set CARBONCAST_DATA_ROOT (see README)."
        ))
    file_list1 = [f for f in os.listdir(path) if f.endswith("_lifecycle_emissions.csv")]
    file_list2 = [f for f in os.listdir(path) if f.endswith("_direct_emissions.csv")]
    dates_list1 = [f.split('_')[1] for f in file_list1 if len(f.split('_')) >= 2]
    dates_list2 = [f.split('_')[1] for f in file_list2 if len(f.split('_')) >= 2]
    if not dates_list1 or not dates_list2:
        raise RealTimeDataNotFoundError(region_code, path, message=(
            f"No lifecycle or direct emissions CSV files in {path}. "
            "Expected names: <region>_<date>_lifecycle_emissions.csv and _direct_emissions.csv"
        ))
    latest_date1, latest_date2 = max(dates_list1), max(dates_list2)
    csv_file1 = os.path.join(path, f'{region_code}_{latest_date1}_lifecycle_emissions.csv')
    csv_file2 = os.path.join(path, f'{region_code}_{latest_date2}_direct_emissions.csv')
    return csv_file1, csv_file2


def get_CI_forecasts_csv_file(region_code, date):
    path = os.path.abspath(os.path.join(os.getcwd(),'real_time',region_code))
    i = 0 
    numFiles = len(os.listdir(path))
    csv_file_l= None
    csv_file_d = None
    for file in os.listdir(path):
        #print("this is printing file:",file)
        if(i ==numFiles-1):
            print(i, file, date)
        i+=1 
        if file.endswith(f"lifecycle_CI_forecasts_{date}.csv"):
            csv_file_l = os.path.join(path, file)
        elif file.endswith(f"direct_CI_forecasts_{date}.csv"):
            csv_file_d = os.path.join(path, file)
    if (csv_file_l is None): # file not found
        #csv_file_l = os.path.join(path, f"{region_code}_lifecycle_CI_forecasts_2023-08-07.csv")
        latestdate = list()
        for filename in os.listdir(path):
            if "lifecycle_CI_forecast" in filename:
                latestdate.append(filename)
                print("this is the latestdate1:", latestdate[-1])

        csv_file_l = os.path.join(path,latestdate[-1])
    if (csv_file_d is None): # file not found
       #csv_file_d = os.path.join(path, f"{region_code}_direct_CI_forecasts_2023-08-07.csv")
       latestdate2 = list()
       for filename in os.listdir(path):
            if "direct_CI_forecasts" in filename:
                latestdate2.append(filename)
                print("this is the latestdate2:", latestdate2[-1])
                csv_file_d = os.path.join(path, latestdate2[-1])
    
    return csv_file_l, csv_file_d



def get_actual_value_file_by_date(region_code, date):
    path = os.path.abspath(os.path.join(os.getcwd(),'real_time',region_code))
    i = 0
    numFiles = len(os.listdir(path))
    csv_file_a = None
    csv_file_b = None
    for file in os.listdir(path):
        if(i, file, date):
            print(i, file, date)
        i += 1
        if file.endswith(f"_{date}_lifecycle_emissions.csv"):
            csv_file_a = os.path.join(path, file)
            print(csv_file_a)
        elif file.endswith(f"_{date}_direct_emissions.csv"):
            csv_file_b = os.path.join(path, file)
            print(csv_file_b)
    if (csv_file_a is None): # file not found
        latestdate3 = list()
        for filename in os.listdir(path):
            if "lifecycle_emissions" in filename:
                latestdate3.append(filename)
                print("this is the latestdate3:", latestdate3[-1])
        csv_file_a = os.path.join(path,latestdate3[-1] )

    if (csv_file_b is None): # file not found
        latestdate4 = list()
        for filename in os.listdir(path):
            if "direct_emissions" in filename:
                latestdate4.append(filename)
                print("this is the latestdate4:", latestdate4[-1])
        csv_file_b = os.path.join(path,latestdate4[-1])

    print(csv_file_a, csv_file_b)
    return csv_file_a, csv_file_b

def get_energy_forecasts_csv_file(region_code, date):
    path = os.path.abspath(os.path.join(os.getcwd(),'real_time',region_code))
    for file in os.listdir(path):
        if file.endswith(f"_96hr_forecasts_{date}.csv"):
            e_forecast_csv_file = os.path.join(path, file)
    return e_forecast_csv_file


def get_ci_forecast_series(region_code, emission_type='lifecycle', date=None):
    """
    Load 96-hour carbon intensity forecast for a region for use in scheduling.
    Returns (times, tco): list of 96 datetime strings (ISO), list of 96 floats (gCO2/kWh).

    emission_type: 'lifecycle' or 'direct'
    date: YYYY-MM-DD or None for today UTC. Forecast file is chosen for this date or latest.
    """
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    path_real = os.path.abspath(os.path.join(os.getcwd(), 'real_time', region_code))
    csv_path = None

    if os.path.isdir(path_real):
        try:
            csv_l, csv_d = get_CI_forecasts_csv_file(region_code, date)
            candidate = csv_l if emission_type == 'lifecycle' else csv_d
            if candidate and os.path.isfile(candidate):
                csv_path = candidate
        except (FileNotFoundError, IndexError, OSError):
            pass

    # Fallback: CI_forecast_data (second-tier output) next to src
    if csv_path is None or not os.path.isfile(csv_path):
        cwd = os.getcwd()
        # CarbonCastAPI when run from manage.py; go up to repo root and try CI_forecast_data
        for base in [cwd, os.path.dirname(cwd), os.path.join(os.path.dirname(cwd), '..')]:
            ci_dir = os.path.join(base, 'CI_forecast_data', region_code)
            if not os.path.isdir(ci_dir):
                continue
            for f in os.listdir(ci_dir):
                if emission_type == 'lifecycle' and 'lifecycle' in f and '96hr' in f and f.endswith('.csv'):
                    csv_path = os.path.join(ci_dir, f)
                    break
                if emission_type == 'direct' and 'direct' in f and '96hr' in f and f.endswith('.csv'):
                    csv_path = os.path.join(ci_dir, f)
                    break
            if csv_path and os.path.isfile(csv_path):
                break

    if not csv_path or not os.path.isfile(csv_path):
        raise RealTimeDataNotFoundError(
            region_code,
            path_real,
            message=(
                f"No {emission_type} carbon intensity forecast found for region '{region_code}' "
                f"(date={date}). Ensure real_time/<region>/ has *{emission_type}_CI_forecasts*.csv "
                "or CI_forecast_data/<region> has *96hr*CI*forecasts*.csv."
            ),
        )

    times = []
    tco = []
    time_col = 0
    value_col = 3

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header:
            h = [str(c).lower() for c in header]
            for i, c in enumerate(h):
                if 'datetime' in c or ('time' in c and 'creation' not in c):
                    time_col = i
                if 'forecast' in c or ('carbon' in c and 'actual' not in c):
                    value_col = i
        for row in reader:
            if len(row) <= max(time_col, value_col):
                continue
            try:
                times.append(row[time_col].strip())
                tco.append(float(row[value_col]))
            except (ValueError, IndexError):
                continue
            if len(times) >= 96:
                break

    if len(times) < 96:
        raise RealTimeDataNotFoundError(
            region_code,
            csv_path,
            message=f"Forecast file has only {len(times)} rows; need at least 96.",
        )

    return times[:96], tco[:96]


def get_best_slot_indices_for_job(L, deadline_index, is_continuous, tco):
    """
    Compute best hour-slot indices and total cost for a job (provides times/info for scheduling).
    Does not perform any scheduling; returns (chosen_indices, total_cost) or None.
    """
    N = min(deadline_index, 96)
    if N < L:
        return None
    tco = tco[:N]
    if is_continuous:
        best_start = 0
        best_cost = float("inf")
        for start in range(0, N - L + 1):
            cost_sum = sum(tco[start + k] for k in range(L))
            if cost_sum < best_cost:
                best_cost = cost_sum
                best_start = start
        return [best_start + k for k in range(L)], best_cost
    pairs = [(tco[i], i) for i in range(N)]
    pairs.sort()
    chosen_indices = sorted([pairs[j][1] for j in range(L)])
    total_cost = sum(pairs[j][0] for j in range(L))
    return chosen_indices, total_cost


