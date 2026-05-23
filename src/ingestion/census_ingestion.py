import requests
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("CENSUS_API_KEY")
BASE_URL = "https://api.census.gov/data"

STATE_FIPS = "47"  # Tennessee

COUNTIES = {
    "Davidson":   "037",
    "Williamson": "187",
    "Rutherford": "149",
    "Montgomery": "125",
    "Wilson":     "189",
    "Sumner":     "165",
    "Maury":      "119",
    "Putnam":     "141",
    "Dickson":    "043",
    "Robertson":  "147",
    "Bedford":    "003",
    "Coffee":     "031",
}

# ACS 5-year variables
VARIABLES = {
    "B01003_001E": "total_population",
    "B19013_001E": "median_household_income",
    "B17001_002E": "population_below_poverty",
    "B23025_004E": "employed_population",
    "B23025_005E": "unemployed_population",
    "B24081_001E": "self_employed_count",
    "B08301_001E": "total_workers",
}

YEARS = [2019, 2020, 2021, 2022, 2023]


def fetch_acs5(year: int) -> list:
    county_fips = ",".join(COUNTIES.values())
    var_list = "NAME," + ",".join(VARIABLES.keys())

    params = {
        "get": var_list,
        "for": f"county:{county_fips}",
        "in": f"state:{STATE_FIPS}",
    }

    response = requests.get(f"{BASE_URL}/{year}/acs/acs5", params=params, timeout=30)
    response.raise_for_status()
    raw = response.json()

    headers = raw[0]
    rows = []
    for row in raw[1:]:
        record = dict(zip(headers, row))
        record["year"] = year
        # Map FIPS back to county name
        fips_to_name = {v: k for k, v in COUNTIES.items()}
        record["county_name"] = fips_to_name.get(record.get("county"), "Unknown")
        # Rename variables to readable names
        for code, readable in VARIABLES.items():
            if code in record:
                record[readable] = record.pop(code)
        rows.append(record)

    return rows


def run():
    output_dir = Path("raw_data/census")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_records = []

    for year in YEARS:
        print(f"Fetching ACS 5-year data for {year}...")
        try:
            records = fetch_acs5(year)
            all_records.extend(records)
            for r in records:
                print(f"  {r['county_name']}: population={r.get('total_population')}, "
                      f"median_income={r.get('median_household_income')}")
        except requests.RequestException as e:
            print(f"  {year}: ERROR - {e}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"census_acs5_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_records, f, indent=2)

    print(f"\nDone. {len(all_records)} records saved to {output_file}")


if __name__ == "__main__":
    run()
