"""
Hlavní vstupní bod scraperu.
Spouští stahování, parsování a ukládání dat o bazarových noteboocích z Alza.cz.
"""

import logging
import sys
from pathlib import Path

from scraper import AlzaScraper
from parser import AlzaParser
from utils import save_to_csv, setup_logging

TARGET_URL_TEMPLATE = (
    "https://www.alza.cz/notebooky/bazar-pouzite-zbozi/"
    "u18842920.htm?o={page}&s=0"
)
MAX_PAGES = 60          
MIN_RECORDS = 1500      
OUTPUT_FILE = Path("data/raw/notebooks_raw.csv")


def main() -> None:
    setup_logging()
    log = logging.getLogger(__name__)

    log.info("=== Spouštím scraper Alza.cz bazar – notebooky ===")

    scraper = AlzaScraper()
    parser = AlzaParser()

    all_records = []
    page = 1

    while page <= MAX_PAGES:
        url = TARGET_URL_TEMPLATE.format(page=page)
        log.info("Stahuji stránku %d / %d: %s", page, MAX_PAGES, url)

        html = scraper.fetch_page(url)
        if html is None:
            log.warning("Stránka %d se nepodařila stáhnout, přeskakuji.", page)
            page += 1
            continue

        records = parser.parse_listing_page(html)
        if not records:
            log.info("Stránka %d neobsahuje žádné produkty – konec listingu.", page)
            break

        all_records.extend(records)
        log.info(
            "Stránka %d: +%d záznamů (celkem: %d)",
            page, len(records), len(all_records),
        )
        page += 1

    scraper.close()

    if not all_records:
        log.error("Nebyla získána žádná data. Zkontrolujte připojení a selektory.")
        sys.exit(1)

    if len(all_records) < MIN_RECORDS:
        log.warning(
            "Získáno pouze %d záznamů (minimum je %d). "
            "Zkuste zvýšit MAX_PAGES nebo zkontrolujte strukturu webu.",
            len(all_records), MIN_RECORDS,
        )

    save_to_csv(all_records, OUTPUT_FILE)
    log.info("Hotovo! Celkem uloženo %d záznamů do %s", len(all_records), OUTPUT_FILE)


if __name__ == "__main__":
    main()
