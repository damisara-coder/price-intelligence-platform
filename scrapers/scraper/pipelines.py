from datetime import datetime
from itemadapter import ItemAdapter
import re

class ScraperPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # ✅ Nettoyer le prix — ex: "1,979.00 Dhs" → 1979.0
        price = adapter.get("price", "")
        if price:
            # Étape 1 : enlever les virgules de milliers
            # Étape 2 : garder uniquement chiffres et point décimal
            price_clean = re.sub(r"[^\d.]", "", price.replace(",", ""))
            try:
                adapter["price"] = float(price_clean)
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