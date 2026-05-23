import requests
import json
import os
from datetime import datetime
from pathlib import Path

BASE_URL = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"

TN_COUNTIES_ZIP = {
    "DAVIDSON":   ["37201", "37203", "37204", "37205", "37206", "37207", "37208",
                   "37209", "37210", "37211", "37212", "37213", "37214", "37215",
                   "37216", "37217", "37218", "37219", "37220", "37221"],
    "WILLIAMSON": ["37027", "37064", "37067", "37069", "37135", "37174", "37179"],
    "RUTHERFORD": ["37037", "37085", "37086", "37127", "37128", "37129", "37130",
                   "37132", "37149", "37153"],
    "MONTGOMERY": ["37040", "37041", "37042", "37043", "37044"],
    "WILSON":     ["37087", "37090"],
    "SUMNER":     ["37066", "37075", "37148"],
    "MAURY":      ["38401", "38402", "38403", "38476"],
    "PUTNAM":     ["38501", "38502", "38503", "38504", "38506"],
    "DICKSON":    ["37055", "37056"],
    "ROBERTSON":  ["37172", "37073"],
    "BEDFORD":    ["37160", "37162"],
    "COFFEE":     ["37388", "37355"],
}

ALL_ZIP_CODES = [z for zips in TN_COUNTIES_ZIP.values() for z in zips]


def fetch_complaints(zip_code: str, date_min: str = "2019-01-01", page_size: int = 100) -> list:
    complaints = []
    params = {
        "zip_code": zip_code,
        "date_received_min": date_min,
        "size": page_size,
        "from": 0,
        "sort": "created_date_desc",
    }

    while True:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break

        complaints.extend([h["_source"] for h in hits])

        total = data["hits"]["total"]["value"]
        params["from"] += page_size
        if params["from"] >= total:
            break

    return complaints


def run():
    output_dir = Path("raw_data/cfpb")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_complaints = []

    for county, zip_codes in TN_COUNTIES_ZIP.items():
        print(f"Fetching complaints for {county} county...")
        county_complaints = []

        for zip_code in zip_codes:
            try:
                results = fetch_complaints(zip_code)
                for r in results:
                    r["county"] = county
                county_complaints.extend(results)
                print(f"  {zip_code}: {len(results)} complaints")
            except requests.RequestException as e:
                print(f"  {zip_code}: ERROR - {e}")

        all_complaints.extend(county_complaints)
        print(f"  {county} total: {len(county_complaints)}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"cfpb_complaints_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(all_complaints, f, indent=2)

    print(f"\nDone. {len(all_complaints)} total complaints saved to {output_file}")


if __name__ == "__main__":
    run()
