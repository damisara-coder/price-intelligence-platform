import scrapy
from scraper.items import ProductItem
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

class AvitoSpider(scrapy.Spider):
    name = "avito"
    LIMIT_PER_CATEGORY = 250
    DEBUG_HTML = True

    TITLE_SELECTORS = [
        "article h3",
        "article h2",
        "[class*='sc-'] h3",
        "[class*='sc-'] p",
        "a[href*='/vi/'] h3",
        "a[href*='/vi/'] p",
        "div[class*='listing'] h3",
        "div[class*='item'] h3",
        "div[class*='card'] h3",
        "div[class*='Card'] h3",
        "div[class*='product'] h3",
        "main h3",
        "main p",
    ]

    PRICE_SELECTORS = [
        "p[class*='price']",
        "span[class*='price']",
        "[data-testid='listing-price']",
        "[class*='Price']",
        "[class*='price'] span",
        "article [class*='price']",
        "article [class*='Price']",
        "[class*='sc-'] [class*='price']",
        "[class*='sc-'] [class*='Price']",
    ]

    categories = {
        "smartphones": "https://www.avito.ma/fr/maroc/t%C3%A9l%C3%A9phones/_vendre?delivery=true",
        "laptops":     "https://www.avito.ma/fr/maroc/ordinateurs_portables/ordinateurs--%C3%A0_vendre?delivery=true",
        "tv":          "https://www.avito.ma/fr/maroc/t%C3%A9l%C3%A9visions/tv--%C3%A0_vendre?delivery=true",
        "vetements":   "https://www.avito.ma/fr/maroc/vetements-%C3%A0_vendre?delivery=true",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--lang=fr-MA")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.counts = {cat: 0 for cat in self.categories}
        self._title_selector = None
        self._price_selector = None

    def start_requests(self):
        for category in self.categories:
            yield scrapy.Request(
                url="https://www.avito.ma",
                callback=self.parse,
                meta={"category": category},
                dont_filter=True
            )

    def _wait_for_page(self):
        """Attendre que le body Next.js soit hydraté avec du contenu."""
        # Étape 1 : laisser le JS initial s'exécuter
        time.sleep(3)

        # Étape 2 : attendre que le body contienne du texte substantiel
        try:
            WebDriverWait(self.driver, 20).until(
                lambda d: len(
                    d.find_element(By.TAG_NAME, "body").text.strip()
                ) > 200
            )
        except Exception:
            pass

        # Étape 3 : pause supplémentaire pour l'hydratation React/Next.js
        time.sleep(5)

    def _probe_selectors(self):
        """Tester chaque sélecteur et retourner le premier qui fonctionne."""
        found_title = None
        for sel in self.TITLE_SELECTORS:
            try:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                self.logger.info(f"  Sélecteur '{sel}' → {len(els)} éléments")
                if els and not found_title:
                    found_title = sel
            except Exception as e:
                self.logger.warning(f"  Sélecteur invalide '{sel}': {e}")

        found_price = None
        for sel in self.PRICE_SELECTORS:
            try:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                self.logger.info(f"  Prix sélecteur '{sel}' → {len(els)} éléments")
                if els and not found_price:
                    found_price = sel
            except Exception as e:
                self.logger.warning(f"  Sélecteur prix invalide '{sel}': {e}")

        return found_title, found_price

    def _dump_body_html(self, label=""):
        """Dumper uniquement le contenu <body>, 5000 premiers caractères."""
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            html = body.get_attribute("innerHTML")
            self.logger.warning(f"=== BODY HTML [{label}] (5000 premiers chars) ===")
            self.logger.warning(html[:5000])
            self.logger.warning("=== FIN BODY ===")
        except Exception as e:
            self.logger.warning(f"Impossible de récupérer le body: {e}")

    def parse(self, response):
        category = response.meta["category"]
        base_url = self.categories[category]
        page = 1

        while self.counts[category] < self.LIMIT_PER_CATEGORY:
            sep = "&" if "?" in base_url else "?"
            page_url = f"{base_url}{sep}o={page}"

            self.driver.get(page_url)

            # Attendre le rendu complet de Next.js
            self._wait_for_page()

            # Découverte des sélecteurs (une seule fois au démarrage)
            if self._title_selector is None:
                self.logger.info(f"[{category}] Sondage des sélecteurs page {page}...")
                t_sel, p_sel = self._probe_selectors()

                if t_sel:
                    self._title_selector = t_sel
                    self._price_selector = p_sel
                    self.logger.info(f"✅ Sélecteur titre trouvé : {t_sel}")
                    self.logger.info(f"✅ Sélecteur prix trouvé  : {p_sel}")
                else:
                    self.logger.warning(
                        f"❌ Aucun sélecteur ne correspond — dump HTML body pour inspection"
                    )
                    self._dump_body_html(category)
                    # Arrêter uniquement cette catégorie, pas tout le spider
                    break

            titles = self.driver.find_elements(By.CSS_SELECTOR, self._title_selector)
            prices = (
                self.driver.find_elements(By.CSS_SELECTOR, self._price_selector)
                if self._price_selector
                else []
            )

            self.logger.info(f"[{category}] Page {page} — {len(titles)} produits trouvés")

            if not titles:
                if self.DEBUG_HTML:
                    self._dump_body_html(f"{category}-page{page}")
                self.logger.info(f"[{category}] Aucun produit — arrêt")
                break

            for i, title_el in enumerate(titles):
                if self.counts[category] >= self.LIMIT_PER_CATEGORY:
                    break
                try:
                    name = title_el.text.strip()
                    if not name:
                        continue

                    # Récupérer le prix
                    price = ""
                    if i < len(prices):
                        price = prices[i].text.strip()

                    # Récupérer l'URL du produit
                    try:
                        parent = title_el.find_element(By.XPATH, "./ancestor::a[1]")
                        url_product = parent.get_attribute("href")
                    except Exception:
                        url_product = page_url

                    item = ProductItem()
                    item["name"]      = name
                    item["price"]     = price
                    item["category"]  = category
                    item["source"]    = "avito"
                    item["url"]       = url_product
                    item["timestamp"] = datetime.utcnow().isoformat()

                    self.counts[category] += 1
                    yield item

                except Exception as e:
                    self.logger.warning(f"Erreur produit: {e}")
                    continue

            self.logger.info(
                f"[{category}] Total: {self.counts[category]}/{self.LIMIT_PER_CATEGORY}"
            )
            page += 1
            time.sleep(3)

    def closed(self, reason):
        self.driver.quit()