import pandas as pd
from pathlib import Path

def save_to_csv(data):
    df = pd.DataFrame(data)

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "notebooks_raw.csv"
    df.to_csv(output_file, index=False)
