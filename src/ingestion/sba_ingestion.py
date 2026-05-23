import pandas as pd
import json
from datetime import datetime
from pathlib import Path

TARGET_COUNTIES = [
    "DAVIDSON", "WILLIAMSON", "RUTHERFORD", "MONTGOMERY",
    "WILSON", "SUMNER", "MAURY", "PUTNAM",
    "DICKSON", "ROBERTSON", "BEDFORD", "COFFEE",
]

FILES = {
    "7a_2010_2019": "raw_data/sba/foia-7a-fy2010-fy2019-as-of-251231.csv",
    "7a_2020_present": "raw_data/sba/foia-7a-fy2020-present-as-of-251231.csv",
    "504": "raw_data/sba/foia-504-fy2010-present-asof-251231.csv",
}


def load_and_filter(filepath: str, program: str) -> pd.DataFrame:
    print(f"Loading {program} data from {filepath}...")
    df = pd.read_csv(filepath, low_memory=False)
    print(f"  Total rows: {len(df):,}")

    df_tn = df[
        (df["projectstate"].str.upper() == "TN") &
        (df["projectcounty"].str.upper().isin(TARGET_COUNTIES))
    ].copy()

    df_tn["program_type"] = program
    print(f"  Middle TN rows: {len(df_tn):,}")
    return df_tn


def run():
    output_dir = Path("raw_data/sba")
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    for program, filepath in FILES.items():
        path = Path(filepath)
        if not path.exists():
            print(f"File not found, skipping: {filepath}")
            continue
        df = load_and_filter(filepath, program)
        frames.append(df)

    if not frames:
        print("No data loaded.")
        return

    combined = pd.concat(frames, ignore_index=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"sba_midtenn_{timestamp}.json"
    combined.to_json(output_file, orient="records", indent=2)

    print(f"\nDone. {len(combined):,} total loans saved to {output_file}")
    print("\nBreakdown by county:")
    print(combined.groupby(["projectcounty", "program_type"]).size().to_string())


if __name__ == "__main__":
    run()
