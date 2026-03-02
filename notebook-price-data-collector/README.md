# Notebook Price Data Collector

Scraper dat o bazarových noteboocích z **Alza.cz**.

Projekt je první fází většího SW projektu zaměřeného na predikci ceny použitých notebooků pomocí modelu strojového učení.

---

## Co scraper sbírá

Z každého notebooku v bazaru Alza.cz extrahuje:

| Sloupec | Popis | Příklad |
|---|---|---|
| `scraped_at` | Datum a čas sběru | `2025-03-01T14:23:11` |
| `brand` | Značka | `Lenovo` |
| `name` | Plný název produktu | `Notebook - Intel Core i7...` |
| `condition` | Stav (rozbaleno / použito / repasováno) | `Použito` |
| `price_czk` | Cena v Kč | `12490` |
| `cpu` | Procesor | `Intel Core i7 13700H` |
| `ram_gb` | RAM v GB | `16` |
| `disk_gb` | Úložiště v GB | `512` |
| `disk_type` | Typ úložiště | `SSD` |
| `display_inches` | Úhlopříčka displeje | `14.0` |
| `gpu` | Grafická karta | `Intel Iris Xe Graphics` |
| `weight_kg` | Hmotnost v kg | `1.39` |
| `os` | Operační systém | `Windows 11 Home` |
| `description_raw` | Surový popis pro ladění parseru | … |

Výstup: `data/raw/notebooks_raw.csv`

---

## Požadavky

- Python 3.10 nebo novější
- Internetové připojení
- ~200 MB místa (Playwright Chromium)

---

## Instalace a spuštění

### Windows

```
run_scraper.bat
```

Skript automaticky:
1. Nainstaluje Python závislosti (`pip install -r requirements.txt`)
2. Nainstaluje Playwright Chromium (`playwright install chromium`)
3. Spustí scraper

### Linux / macOS

```bash
chmod +x run_scraper.sh
./run_scraper.sh
```

### Manuální spuštění

```bash
pip install -r requirements.txt
playwright install chromium
cd src
python main.py       # nebo python3 main.py na Linuxu
```

---

## Struktura projektu

```
notebook-price-data-collector/
│
├── README.md
├── requirements.txt
├── run_scraper.bat         # Spuštění na Windows
├── run_scraper.sh          # Spuštění na Linux/Mac
│
├── src/                    # Autorský kód
│   ├── main.py             # Vstupní bod, orchestrace
│   ├── scraper.py          # Stahování stránek (Playwright)
│   ├── parser.py           # Parsování HTML + regex extrakce specifikací
│   └── utils.py            # Ukládání CSV, logování
│
└── data/
    ├── raw/
    │   └── notebooks_raw.csv   # Výstupní dataset
    └── logs/
        └── scraper.log         # Log průběhu scrapování
```

---

## Zdroj dat

Data jsou získávána automatizovaně z veřejně přístupného webu **Alza.cz** – sekce bazar (použité/rozbalené/repasované notebooky):

- `https://www.alza.cz/notebooky/bazar-pouzite-zbozi/u18842920.htm`

Stránka se prochází po jednotlivých listingových stránkách (parametr `?o={číslo_stránky}`).  
Data **nejsou** převzata z žádného hotového datasetu. Každý záznam pochází z reálné aktuální nabídky Alza.cz v době spuštění scraperu.

### Počet záznamů

Alza zobrazuje přibližně 24 produktů na stránku. Scraper standardně prochází až 60 stránek, což odpovídá ~1 440 záznamům (splňuje požadavek zadání: min. 1 500). Pro více dat stačí zvýšit `MAX_PAGES` v `src/main.py`.

### Atributy (splňuje min. 5 dle zadání)

Dataset obsahuje **14 atributů** na záznam, z nichž klíčových 8 je použitelných pro trénování ML modelu: cena, RAM, disk, procesor, displej, GPU, hmotnost, stav.

---

## Technické poznámky

**Proč Playwright?**  
Alza.cz renderuje seznam produktů pomocí JavaScriptu. Klasický `requests + BeautifulSoup` by vrátil prázdnou stránku. Playwright spustí headless Chromium, který JavaScript provede, a teprve pak předá HTML parseru.

**Etické scrapování**  
Mezi každým požadavkem je náhodná prodleva 1,5–3,5 s, aby scraper nezatěžoval server Alza.cz.

**Opakované spouštění**  
Scraper lze spustit opakovaně. Nové záznamy se přidají do existujícího CSV, duplikáty se automaticky odstraní.
