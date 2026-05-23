import requests
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("FRED_API_KEY")
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    # National interest rates
    "FEDFUNDS":     "federal_funds_rate",
    "DPRIME":       "bank_prime_loan_rate",
    "MORTGAGE30US": "mortgage_rate_30yr",
    # Tennessee state level
    "TNUR":         "tennessee_unemployment_rate",
    "TNRGSP":       "tennessee_real_gdp",
    "TNPCPI":       "tennessee_per_capita_income",
    "TNSLGRTAX":    "tennessee_tax_revenue",
}

START_DATE = "2019-01-01"
END_DATE   = datetime.now().strftime("%Y-%m-%d")


def fetch_series(series_id: str) -> list:
    params = {
        "series_id":        series_id,
        "api_key":          API_KEY,
        "file_type":        "json",
        "observation_start": START_DATE,
        "observation_end":   END_DATE,
    }
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("observations", [])


def run():
    output_dir = Path("raw_data/fred")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_data = {}

    for series_id, label in SERIES.items():
        print(f"Fetching {series_id} ({label})...")
        try:
            observations = fetch_series(series_id)
            all_data[series_id] = {
                "label": label,
                "observations": observations,
            }
            print(f"  {len(observations)} observations")
        except requests.RequestException as e:
            print(f"  ERROR: {e}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"fred_data_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=2)

    print(f"\nDone. {len(all_data)} series saved to {output_file}")


if __name__ == "__main__":
    run()
