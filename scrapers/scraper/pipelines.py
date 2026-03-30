from datetime import datetime
from itemadapter import ItemAdapter

class ScraperPipeline:
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # ✅ Nettoyer le prix — enlever les symboles et espaces
        price = adapter.get("price", "")
        if price:
            price = price.replace("MAD", "").replace("DH", "")\
                         .replace("$", "").replace(",", "")\
                         .replace("\xa0", "").strip()
            try:
                adapter["price"] = float(price)
            except ValueError:
                adapter["price"] = None

        # ✅ Nettoyer le nom — enlever les espaces inutiles
        name = adapter.get("name", "")
        if name:
            adapter["name"] = " ".join(name.split())

        # ✅ Ajouter le timestamp si absent
        if not adapter.get("timestamp"):
            adapter["timestamp"] = datetime.utcnow().isoformat()

        return item