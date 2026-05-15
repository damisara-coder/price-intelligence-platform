# Nom du projet
BOT_NAME = "scraper"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

# ✅ Respecter le robots.txt de chaque site
ROBOTSTXT_OBEY = True

# ✅ Délai entre chaque requête (2 secondes) — pour ne pas surcharger les sites
DOWNLOAD_DELAY = 2

# ✅ Simuler un vrai navigateur pour éviter les blocages
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

# ✅ Nombre maximum de requêtes simultanées
CONCURRENT_REQUESTS = 4

# ✅ Format de sortie des données
FEEDS = {
    "data/%(name)s_%(time)s.json": {
        "format": "json",
        "encoding": "utf8",
        "indent": 2,
    }
}

# ✅ Activer le pipeline pour traiter les données
ITEM_PIPELINES = {
    "scraper.pipelines.ScraperPipeline": 300,
}

LOG_LEVEL = "INFO"