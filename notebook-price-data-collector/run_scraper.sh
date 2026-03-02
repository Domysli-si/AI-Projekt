#!/bin/bash
set -e

echo "=== Alza.cz Notebook Bazar Scraper ==="

if ! command -v python3 &> /dev/null; then
    echo "CHYBA: python3 nenalezen. Nainstaluj Python 3.10+."
    exit 1
fi

echo "Instaluji závislosti..."
pip3 install -r requirements.txt --quiet

echo "Instaluji Playwright Chromium..."
playwright install chromium

echo "Spouštím scraper..."
cd src
python3 main.py
cd ..

echo ""
echo "=== Hotovo. Zkontroluj data/raw/notebooks_raw.csv ==="
