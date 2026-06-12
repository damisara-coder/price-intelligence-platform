import scrapy
from scraper.items import ProductItem
from datetime import datetime
import json


class ZaraSpider(scrapy.Spider):
    name = "zara"
    allowed_domains = ["zara.com"]
    LIMIT_PER_CATEGORY = 300

    categories = {
        "vetements": {
            "category_id": "2546081",
            "url": "https://www.zara.com/ma/fr/category/2546081/products?ajax=true",
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counts = {cat: 0 for cat in self.categories}

    def start_requests(self):
        for category, info in self.categories.items():
            yield scrapy.Request(
                url=f"{info['url']}&offset=0&limit=40",
                callback=self.parse,
                meta={
                    "category": category,
                    "offset": 0,
                    "base_url": info["url"]
                },
                headers={
                    "Accept": "application/json",
                    "Referer": "https://www.zara.com/ma/fr/",
                }
            )

    def parse(self, response):
        category = response.meta["category"]
        offset = response.meta["offset"]
        base_url = response.meta["base_url"]

        try:
            data = json.loads(response.text)
        except Exception as e:
            self.logger.error(f"Erreur JSON: {e}")
            return

        # ✅ Extraire les produits depuis la réponse JSON
        product_groups = data.get("productGroups", [])

        produits_page = 0
        for group in product_groups:
            for element in group.get("elements", []):
                for component in element.get("commercialComponents", []):
                    if self.counts[category] >= self.LIMIT_PER_CATEGORY:
                        return

                    if component.get("type") != "Product":
                        continue

                    # ✅ Nom
                    name = component.get("name", "").strip()
                    if not name:
                        continue

                    # ✅ Prix — divisé par 100 pour avoir le vrai prix
                    price_raw = component.get("price", None)
                    price = round(price_raw / 100, 2) if price_raw else None

                    # ✅ Ignorer sans prix
                    if price is None:
                        continue

                    # ✅ URL produit

                    product_id = component.get("id", "")
                    url_product = f"https://www.zara.com/ma/fr/-p{str(product_id).zfill(8)}.html"

                    item = ProductItem()
                    item["name"] = name
                    item["price"] = price
                    item["category"] = category
                    item["source"] = "zara"
                    item["url"] = url_product
                    item["timestamp"] = datetime.utcnow().isoformat()

                    self.counts[category] += 1
                    produits_page += 1
                    yield item

        self.logger.info(f"[{category}] offset {offset} — {produits_page} produits")
        self.logger.info(f"[{category}] Total: {self.counts[category]}/300")

        # ✅ Page suivante
        if (self.counts[category] < self.LIMIT_PER_CATEGORY
                and produits_page > 0):
            next_offset = offset + 40
            next_url = f"{base_url}&offset={next_offset}&limit=40"
            self.logger.info(f"[{category}] → offset {next_offset}")
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                meta={
                    "category": category,
                    "offset": next_offset,
                    "base_url": base_url
                },
                headers={
                    "Accept": "application/json",
                    "Referer": "https://www.zara.com/ma/fr/",
                }
            )
