import scrapy
from scraper.items import ProductItem
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time

class AvitoSpider(scrapy.Spider):
    name = "avito"
    LIMIT_PER_CATEGORY = 250

    categories = {
        "smartphones": "https://www.avito.ma/fr/maroc/t%C3%A9l%C3%A9phones/_vendre?delivery=true",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
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

    def start_requests(self):
        for category in self.categories:
            yield scrapy.Request(
                url="https://www.avito.ma",
                callback=self.parse,
                meta={"category": category},
                dont_filter=True
            )

    def _wait_for_page(self):
        time.sleep(4)
        try:
            # ✅ Attendre que les prix apparaissent spécifiquement
            WebDriverWait(self.driver, 20).until(
                lambda d: len(d.find_elements(
                    By.CSS_SELECTOR, "span.PuYkS")) > 0
            )
        except Exception:
            pass
        time.sleep(3)

    def parse(self, response):
        category = response.meta["category"]
        base_url = self.categories[category]
        page = 1

        while self.counts[category] < self.LIMIT_PER_CATEGORY:
            sep = "&" if "?" in base_url else "?"
            page_url = f"{base_url}{sep}o={page}"

            self.logger.info(f"[{category}] Page {page}")
            self.driver.get(page_url)
            self._wait_for_page()

            # ✅ Sélecteurs exacts trouvés par inspection
            names  = self.driver.find_elements(By.CSS_SELECTOR, "p.iHApav")
            prices = self.driver.find_elements(By.CSS_SELECTOR, "span.PuYkS")
            links  = self.driver.find_elements(By.CSS_SELECTOR, "a.jZXrfL")

            self.logger.info(f"[{category}] {len(names)} noms | {len(prices)} prix | {len(links)} liens")

            if not names:
                self.logger.warning(f"[{category}] Aucun produit — arrêt")
                break

            for i, name_el in enumerate(names):
                if self.counts[category] >= self.LIMIT_PER_CATEGORY:
                    break
                try:
                    name = name_el.text.strip()
                    if not name or len(name) < 3:
                        continue

                    # ✅ Prix
                    price = None
                    if i < len(prices):
                        price_text = prices[i].text.strip()\
                            .replace(" ", "")\
                            .replace("\xa0", "")\
                            .replace(",", ".")
                        try:
                            price = float(price_text)
                        except:
                            price = None

                    # ✅ URL
                    url_product = ""
                    if i < len(links):
                        url_product = links[i].get_attribute("href")

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
                    self.logger.warning(f"Erreur: {e}")
                    continue

            self.logger.info(f"[{category}] Total: {self.counts[category]}/250")
            page += 1
            time.sleep(3)

    def closed(self, reason):
        self.driver.quit()