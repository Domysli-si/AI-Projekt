@echo off
echo === Alza.cz Notebook Bazar Scraper ===

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo CHYBA: Python neni nalezen. Nainstaluj Python 3.10+ a pridej ho do PATH.
    pause
    exit /b 1
)

echo Instaluji zavislosti...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo CHYBA: Instalace zavislosti selhala.
    pause
    exit /b 1
)

echo Instaluji Playwright Chromium...
playwright install chromium
if %errorlevel% neq 0 (
    echo CHYBA: Instalace Playwright Chromium selhala.
    pause
    exit /b 1
)

echo Spoustim scraper...
cd src
python main.py
cd ..

echo.
echo === Hotovo. Zkontroluj data/raw/notebooks_raw.csv ===
pause
