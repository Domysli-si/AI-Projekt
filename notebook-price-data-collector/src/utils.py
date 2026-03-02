import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd


def setup_logging(log_dir: Path = Path("data/logs")) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "scraper.log"

    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8"),
    ]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def save_to_csv(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    new_df = pd.DataFrame(records)

    if output_path.exists():
        existing_df = pd.read_csv(output_path, encoding="utf-8-sig")
        combined = pd.concat([existing_df, new_df], ignore_index=True)
        combined.drop_duplicates(subset=["name", "price_czk"], inplace=True)
        combined.to_csv(output_path, index=False, encoding="utf-8-sig")
        logging.getLogger(__name__).info(
            "CSV aktualizováno: %d řádků (po deduplikaci).", len(combined)
        )
    else:
        new_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logging.getLogger(__name__).info(
            "CSV vytvořeno: %d řádků → %s", len(new_df), output_path
        )
