# Zdroj dat – popis a dokumentace

## Odkud data pocházejí

Data jsou sbírána automatizovaně z veřejně přístupné sekce **Bazar** na webu **Alza.cz**:

- **URL:** `https://www.alza.cz/notebooky/bazar-pouzite-zbozi/u18842920.htm`
- **Typ dat:** Reálné aktuální nabídky použitých, rozbalených a repasovaných notebooků
- **Způsob sběru:** Automatizovaný web scraping vlastním Python skriptem (Playwright + BeautifulSoup)

## Co je zdrojem každého záznamu

Každý řádek v datasetu odpovídá **jedné reálné nabídce notebooku** v bazaru Alza.cz v době spuštění scraperu. Alza.cz je přímým prodejcem, tzn. ceny a stavy jsou ověřené a odpovídají skutečné dostupnosti zboží na skladě.

## Jak jsou data sbírána

1. Scraper otevře listing stránku bazarových notebooků pomocí headless prohlížeče (Playwright + Chromium).
2. Pro každou stránku listingu (stránkování přes parametr `?o=`) se stáhne HTML po provedení JavaScriptu.
3. Parser (BeautifulSoup + regulární výrazy) extrahuje z každé produktové karty:
   - Název a značku notebooku
   - Cenu v Kč
   - Stav produktu (rozbaleno / použito / repasováno)
   - Technické specifikace z textového popisu: CPU, RAM, disk, displej, GPU, hmotnost, OS

## Proč nejde o hotový dataset

- Data jsou stahována přímo z živého webu Alza.cz v reálném čase při každém spuštění.
- Neexistuje žádný identický veřejně dostupný dataset s těmito daty.
- Záznamy se průběžně mění (nové nabídky, vyprodané kusy, změny cen).
- Skript `src/scraper.py` a `src/parser.py` jsou vlastním autorským dílem.

## Atributy datasetu a jejich původ

| Atribut | Zdroj v HTML | Poznámka |
|---|---|---|
| `scraped_at` | generováno skriptem | čas sběru záznamu |
| `brand` | parsováno z názvu | extrakce regex |
| `name` | `a.name` / `h2.name a` | plný název produktu |
| `condition` | `span.bazar-badge` | stav zboží |
| `price_czk` | `span.price-box__price` | cena v Kč |
| `cpu` | textový popis karty | regex |
| `ram_gb` | textový popis karty | regex `RAM \d+GB` |
| `disk_gb` | textový popis karty | regex `SSD/HDD \d+GB` |
| `disk_type` | textový popis karty | SSD / HDD / eMMC |
| `display_inches` | textový popis karty | regex `\d+"` |
| `gpu` | textový popis karty | regex |
| `weight_kg` | textový popis karty | regex `hmotnost X,XX kg` |
| `os` | textový popis karty | regex |

## Předzpracování (pro ML fázi)

Surová data budou v dalším kroku projektu předzpracována:
- Odstranění záznamů s chybějícími klíčovými hodnotami
- Normalizace názvů CPU (sjednocení zkratek)
- One-hot encoding kategorických proměnných (`disk_type`, `os`, `condition`)
- Škálování numerických hodnot (`price_czk`, `ram_gb`, `disk_gb`, atd.)
- Detekce a ošetření outlierů (extrémní ceny, neobvyklé hodnoty RAM)
