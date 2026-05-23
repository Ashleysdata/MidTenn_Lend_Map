import requests
import json
from datetime import datetime
from pathlib import Path

BASE_URL = "https://banks.data.fdic.gov/api"

TARGET_COUNTIES = [
    "Davidson", "Williamson", "Rutherford", "Montgomery",
    "Wilson", "Sumner", "Maury", "Putnam",
    "Dickson", "Robertson", "Bedford", "Coffee",
]

INSTITUTION_FIELDS = [
    "NAME", "CITY", "STNAME", "COUNTY", "ASSET", "DEP", "NETINC",
    "REPDTE", "ESTYMD", "ENDEFYMD", "ACTIVE", "CERT", "RSSDID",
    "LNLSNET", "LNLSCON", "LNCI", "LNAG",
]

SUMMARY_FIELDS = [
    "REPDTE", "CERT", "ASSET", "DEP", "NETINC", "LNLSNET",
]


def fetch_institutions() -> list:
    county_filter = " OR ".join([f"COUNTY:{c}" for c in TARGET_COUNTIES])
    params = {
        "filters": f"STALP:TN AND ({county_filter})",
        "fields": ",".join(INSTITUTION_FIELDS),
        "limit": 500,
        "output": "json",
    }

    response = requests.get(f"{BASE_URL}/institutions", params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    institutions = [item["data"] for item in data.get("data", [])]
    print(f"Found {len(institutions)} institutions in Middle Tennessee counties")
    return institutions


def fetch_summary_by_county() -> list:
    results = []
    for county in TARGET_COUNTIES:
        params = {
            "filters": f"STALP:TN AND COUNTY:{county}",
            "fields": "REPDTE,CERT,ASSET,DEP,NETINC,LNLSNET",
            "limit": 500,
            "output": "json",
        }
        response = requests.get(f"{BASE_URL}/summary", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        county_data = [item["data"] for item in data.get("data", [])]
        for row in county_data:
            row["county"] = county
        results.extend(county_data)
        print(f"  {county}: {len(county_data)} summary records")

    return results


def run():
    output_dir = Path("raw_data/fdic")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("Fetching FDIC institution data...")
    institutions = fetch_institutions()
    inst_file = output_dir / f"fdic_institutions_{timestamp}.json"
    with open(inst_file, "w") as f:
        json.dump(institutions, f, indent=2)
    print(f"Saved to {inst_file}")

    print("\nFetching FDIC summary data by county...")
    try:
        summary = fetch_summary_by_county()
        summary_file = output_dir / f"fdic_summary_{timestamp}.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Saved to {summary_file}")
    except requests.RequestException as e:
        print(f"Summary fetch failed (endpoint may not support county filter): {e}")

    print(f"\nDone. {len(institutions)} institutions saved.")


if __name__ == "__main__":
    run()
