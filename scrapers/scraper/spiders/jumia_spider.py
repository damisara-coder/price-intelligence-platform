import scrapy
from scraper.items import ProductItem
from datetime import datetime

class JumiaSpider(scrapy.Spider):
    name = "jumia"
    allowed_domains = ["jumia.ma"]
    LIMIT_PER_CATEGORY = 200

    categories = {
    "smartphones": "https://www.jumia.ma/telephone-tablette/?page=1#catalog-listing",
    "laptops":     "https://www.jumia.ma/ordinateurs-pc/?page=1#catalog-listing",
    "tv":          "https://www.jumia.ma/tvs/?page=1#catalog-listing",
    "vetements":   "https://www.jumia.ma/vetements-femme/?page=1#catalog-listing",
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

        products = response.css("article.prd")
        
        self.logger.info(f"[{category}] Page {page} — {len(products)} produits trouvés")

        for product in products:
            if self.counts[category] >= self.LIMIT_PER_CATEGORY:
                return

            item = ProductItem()
            item["name"]      = product.css("h3.name::text").get(default="").strip()
            item["price"]     = product.css("div.prc::text").get(default="").strip()
            item["category"]  = category
            item["source"]    = "jumia"
            item["url"]       = "https://www.jumia.ma" + product.css("a.core::attr(href)").get(default="")
            item["timestamp"] = datetime.utcnow().isoformat()

            self.counts[category] += 1
            yield item

        self.logger.info(f"[{category}] Total jusqu'ici : {self.counts[category]}/200")

        # ✅ Passer à la page suivante manuellement
        if self.counts[category] < self.LIMIT_PER_CATEGORY and len(products) > 0:
            next_page_num = page + 1
            next_url = f"https://www.jumia.ma{response.url.split('jumia.ma')[1].split('?')[0]}?page={next_page_num}#catalog-listing"
            self.logger.info(f"[{category}] → Page {next_page_num}")
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                meta={"category": category, "page": next_page_num},
                dont_filter=True
            )