import scrapy
from datetime import datetime

class ProductItem(scrapy.Item):
    # Nom du produit
    name = scrapy.Field()
    
    # Prix du produit
    price = scrapy.Field()
    
    # Catégorie (smartphones, laptops, tv, vetements)
    category = scrapy.Field()
    
    # Site source (jumia, amazon)
    source = scrapy.Field()
    
    # Lien vers le produit
    url = scrapy.Field()
    
    # Date et heure de collecte
    timestamp = scrapy.Field()