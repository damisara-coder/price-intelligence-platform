import scrapy
from scraper.items import ProductItem
from datetime import datetime

class MicromagmaSpider(scrapy.Spider):
    name = "micromagma"
    allowed_domains = ["micromagma.ma"]
    LIMIT_PER_CATEGORY = 300

    categories = {
        "smartphones": "https://micromagma.ma/smartphones",
        "laptops":     "https://micromagma.ma/laptops",
        "tv":          "https://micromagma.ma/tv",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counts = {cat: 0 for cat in self.categories}

    def start_requests(self):
        for category, url in self.categories.items():
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"category": category, "page": 1},
                dont_filter=True
            )

    def parse(self, response):
        category = response.meta["category"]
        page     = response.meta["page"]

        products = response.css("a[href*='/item/']")

        self.logger.info(f"[{category}] Page {page} — {len(products)} produits trouvés")

        for product in products:
            if self.counts[category] >= self.LIMIT_PER_CATEGORY:
                return

            # ✅ Nom
            name = product.css("p.css-1vkdkjv::text").get(default="").strip()

            # ✅ Ignorer si nom vide
            if not name:
                continue

            item = ProductItem()
            item["name"]      = name
            item["price"]     = product.css("p.css-j7ldfz::text").get(default="").strip()
            item["category"]  = category
            item["source"]    = "micromagma"
            item["url"]       = "https://micromagma.ma" + product.attrib.get("href", "")
            item["timestamp"] = datetime.utcnow().isoformat()

            self.counts[category] += 1
            yield item

        self.logger.info(f"[{category}] Total: {self.counts[category]}/300")

        # ✅ Pagination — s'arrête si :
        # 1. On a atteint 300 produits
        # 2. La page est vide
        # 3. Moins de 20 produits (dernière page)
        if (self.counts[category] < self.LIMIT_PER_CATEGORY
                and len(products) >= 20):
            next_page = page + 1
            next_url = f"{self.categories[category]}?page={next_page}"
            self.logger.info(f"[{category}] → Page {next_page}")
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                meta={"category": category, "page": next_page},
                dont_filter=True
            )
        else:
            self.logger.info(
                f"[{category}] Terminé — {self.counts[category]} produits collectés"
            )