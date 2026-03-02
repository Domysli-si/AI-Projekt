from bs4 import BeautifulSoup

def parse_notebooks(html_pages):
    records = []

    for html in html_pages:
        soup = BeautifulSoup(html, "html.parser")

        record = {
            "brand": None,
            "model": None,
            "ram_gb": None,
            "disk_gb": None,
            "disk_type": None,
            "condition": None,
            "age_years": None,
            "price_czk": None
        }

        records.append(record)

    return records
