import logging
import time
import random

log = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    log.warning(
        "Playwright není nainstalován. "
        "Spusť: pip install playwright && playwright install chromium"
    )


class AlzaScraper:
    """
    Stahuje HTML obsah stránek Alza.cz bazar.

    Playwright – headless Chromium – zajišťuje, že se JavaScript-renderovaný
    obsah (produktové karty) správně načte před parsováním.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    DELAY_MIN = 1.5
    DELAY_MAX = 3.5

    WAIT_FOR_SELECTOR = "div.box"
    NETWORK_TIMEOUT = 30_000  

    def __init__(self) -> None:
        self._pw = None
        self._browser = None
        self._page = None

        if PLAYWRIGHT_AVAILABLE:
            self._init_playwright()
        else:
            raise RuntimeError(
                "Playwright není dostupný. "
                "Nainstaluj jej: pip install playwright && playwright install chromium"
            )

    def _init_playwright(self) -> None:
        """Inicializuje Playwright a otevře headless Chromium."""
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=True)
        self._page = self._browser.new_page(
            user_agent=self.USER_AGENT,
            locale="cs-CZ",
        )
        self._page.route(
            "**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf}",
            lambda route: route.abort(),
        )
        log.info("Playwright inicializován (headless Chromium).")

    def fetch_page(self, url: str) -> str | None:
        """
        Stáhne jednu stránku a vrátí její HTML jako string.
        Při chybě vrátí None.
        """
        try:
            self._page.goto(url, timeout=self.NETWORK_TIMEOUT, wait_until="domcontentloaded")

            try:
                self._page.wait_for_selector(self.WAIT_FOR_SELECTOR, timeout=10_000)
            except PWTimeout:
                log.warning("Selektor '%s' nebyl nalezen na %s", self.WAIT_FOR_SELECTOR, url)

            html = self._page.content()

            time.sleep(random.uniform(self.DELAY_MIN, self.DELAY_MAX))
            return html

        except Exception as exc:
            log.error("Chyba při stahování %s: %s", url, exc)
            return None

    def close(self) -> None:
        """Uzavře prohlížeč a Playwright."""
        try:
            if self._browser:
                self._browser.close()
            if self._pw:
                self._pw.stop()
            log.info("Playwright ukončen.")
        except Exception as exc:
            log.warning("Chyba při zavírání Playwright: %s", exc)
