import scrapy
from scraper.items import ProductItem
from datetime import datetime

class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.fr"]

    # ✅ Les 4 catégories à scraper
    categories = {
        "smartphones": "https://www.amazon.fr/s?k=smartphones",
        "laptops":     "https://www.amazon.fr/s?k=laptops",
        "tv":          "https://www.amazon.fr/s?k=televiseurs",
        "vetements":   "https://www.amazon.fr/s?k=vetements+homme",
    }

    def start_requests(self):
        for category, url in self.categories.items():
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"category": category}
            )

    def parse(self, response):
        category = response.meta["category"]

        # ✅ Chaque produit sur la page
        products = response.css("div[data-component-type='s-search-result']")

        for product in products:
            item = ProductItem()

            item["name"]      = product.css("h2 span::text").get(default="").strip()
            item["price"]     = product.css("span.a-price-whole::text").get(default="").strip()
            item["category"]  = category
            item["source"]    = "amazon"
            item["url"]       = "https://www.amazon.fr" + product.css("h2 a::attr(href)").get(default="")
            item["timestamp"] = datetime.utcnow().isoformat()

            yield item

        # ✅ Passer à la page suivante automatiquement
        next_page = response.css("a.s-pagination-next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse, meta={"category": category})