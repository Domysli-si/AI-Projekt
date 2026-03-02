import re
import logging
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


_RE_RAM = re.compile(r"RAM\s+(\d+)\s*GB", re.IGNORECASE)
_RE_DISK_SIZE = re.compile(r"(SSD|HDD|eMMC)\s+(\d+)\s*GB", re.IGNORECASE)

_RE_CPU = re.compile(
    r"(Intel Core(?:\s+Ultra)?\s+[i\d]\d+[\w\-]*"
    r"|AMD Ryzen\s+\d+\s+\w+"
    r"|Apple\s+M\d+(?:\s+\w+)?"
    r"|Snapdragon\s+[\w\+\-]+"
    r"|Intel\s+Core\s+\d+\s+\w+"
    r"|Qualcomm\s+\w+"
    r"|MediaTek\s+\w+)",
    re.IGNORECASE,
)

_RE_DISPLAY = re.compile(r'(\d+[,.]?\d*)\s*"', re.IGNORECASE)

_RE_GPU = re.compile(
    r"(NVIDIA\s+GeForce\s+[\w\s]+?"
    r"|AMD\s+Radeon\s+[\w\s]+?"
    r"|Intel\s+(?:UHD|Iris\s*Xe|Arc)\s*(?:Graphics)?\s*[\w]*"
    r"|Apple\s+M\d+\s+\w+GPU"
    r"|Qualcomm\s+Adreno\s*\w*)",
    re.IGNORECASE,
)

_RE_WEIGHT = re.compile(r"hmotnost\s+([\d,\.]+)\s*kg", re.IGNORECASE)

_RE_OS = re.compile(
    r"(Windows\s+\d+\s+(?:Home|Pro|S)?"
    r"|macOS"
    r"|Google Chrome OS"
    r"|bez\s+operačního\s+systému)",
    re.IGNORECASE,
)


def _clean(text: str) -> str:
    """Odstraní nadbytečné bílé znaky."""
    return " ".join(text.split()).strip()


def _parse_price(text: str) -> int | None:
    """Převede textovou cenu 'od 12 345,-' na integer."""
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def _parse_spec(description: str) -> dict[str, Any]:
    """
    Z textového popisu produktu extrahuje technické specifikace.
    Vrátí dict s klíči odpovídajícími sloupcům CSV.
    """
    spec: dict[str, Any] = {
        "cpu": None,
        "ram_gb": None,
        "disk_gb": None,
        "disk_type": None,
        "display_inches": None,
        "gpu": None,
        "weight_kg": None,
        "os": None,
    }

    # CPU
    m = _RE_CPU.search(description)
    if m:
        spec["cpu"] = _clean(m.group(0))

    # RAM
    m = _RE_RAM.search(description)
    if m:
        spec["ram_gb"] = int(m.group(1))

    # Disk
    m = _RE_DISK_SIZE.search(description)
    if m:
        spec["disk_type"] = m.group(1).upper()
        spec["disk_gb"] = int(m.group(2))

    # Displej
    m = _RE_DISPLAY.search(description)
    if m:
        spec["display_inches"] = float(m.group(1).replace(",", "."))

    # GPU
    m = _RE_GPU.search(description)
    if m:
        spec["gpu"] = _clean(m.group(0))

    # Váha
    m = _RE_WEIGHT.search(description)
    if m:
        spec["weight_kg"] = float(m.group(1).replace(",", "."))

    # OS
    m = _RE_OS.search(description)
    if m:
        spec["os"] = _clean(m.group(0))

    return spec


class AlzaParser:
    CARD_SELECTORS = [
        "div.box.browsingitem",  
        "div.browsingitem",     
        "div.box",               
    ]

    SEL_NAME = ["a.name", "h2.name a", "span.name"]
    SEL_PRICE = ["span.price-box__price", "strong.price", "div.price-box span"]
    SEL_CONDITION = ["span.bazar-badge", "div.bazar-stav", "span.label-stav"]
    SEL_DESCRIPTION = ["div.nameextc", "p.nameextc", "div.description", "p.shortDesc"]

    def _find_first(self, soup: BeautifulSoup, selectors: list[str]) -> str | None:
        """Vrátí text prvního nalezeného selektoru, nebo None."""
        for sel in selectors:
            el = soup.select_one(sel)
            if el and el.get_text(strip=True):
                return _clean(el.get_text(strip=True))
        return None

    def _find_cards(self, soup: BeautifulSoup) -> list:
        """Najde všechny produktové karty na stránce."""
        for sel in self.CARD_SELECTORS:
            cards = soup.select(sel)
            if cards:
                log.debug("Nalezeno %d karet selektorem '%s'", len(cards), sel)
                return cards
        return []

    def parse_listing_page(self, html: str) -> list[dict[str, Any]]:
        """
        Parsuje jednu HTML stránku listingu a vrátí list záznamů (dict).
        Každý záznam = jeden notebook.
        """
        soup = BeautifulSoup(html, "html.parser")
        cards = self._find_cards(soup)

        if not cards:
            log.warning("Na stránce nebyla nalezena žádná produktová karta.")
            return []

        records = []
        scraped_at = datetime.now().isoformat(timespec="seconds")

        for card in cards:
            try:
                record = self._parse_card(card, scraped_at)
                if record:
                    records.append(record)
            except Exception as exc:
                log.debug("Chyba při parsování karty: %s", exc)

        return records

    def _parse_card(self, card: BeautifulSoup, scraped_at: str) -> dict[str, Any] | None:
        name = self._find_first(card, self.SEL_NAME)
        if not name:
            return None

        name_lower = name.lower()
        if not any(kw in name_lower for kw in ["notebook", "macbook", "chromebook", "tablet"]):
            return None

        # Cena
        price_text = self._find_first(card, self.SEL_PRICE) or ""
        price_czk = _parse_price(price_text)

        # Stav (bazar kategorie: rozbaleno / použito / repasováno)
        condition = self._find_first(card, self.SEL_CONDITION)

        # Popis se specifikacemi (jeden dlouhý řetězec)
        description = self._find_first(card, self.SEL_DESCRIPTION) or ""
        if not description:
            # Zkusíme celý text karty jako fallback
            description = _clean(card.get_text(separator=" "))

        # Parsujeme specifikace z textu popisu
        spec = _parse_spec(description)

        # Značka z názvu produktu
        brand = self._extract_brand(name)

        return {
            "scraped_at": scraped_at,
            "brand": brand,
            "name": name,
            "condition": condition,
            "price_czk": price_czk,
            "cpu": spec["cpu"],
            "ram_gb": spec["ram_gb"],
            "disk_gb": spec["disk_gb"],
            "disk_type": spec["disk_type"],
            "display_inches": spec["display_inches"],
            "gpu": spec["gpu"],
            "weight_kg": spec["weight_kg"],
            "os": spec["os"],
            "description_raw": description,
        }

    @staticmethod
    def _extract_brand(name: str) -> str | None:
        """Odhadne značku notebooku z názvu produktu."""
        brands = [
            "Lenovo", "HP", "Dell", "Asus", "Acer", "Apple",
            "MSI", "Samsung", "Microsoft", "Huawei", "LG",
            "Toshiba", "Sony", "Razer", "Gigabyte",
        ]
        name_lower = name.lower()
        for brand in brands:
            if brand.lower() in name_lower:
                return brand
        return None
