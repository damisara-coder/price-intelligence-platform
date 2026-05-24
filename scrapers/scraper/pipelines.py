from datetime import datetime
from itemadapter import ItemAdapter
import re

class ScraperPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # ✅ Nettoyer le prix — accepte float ET string
        price = adapter.get("price", "")
        if price is not None and price != "":
            if isinstance(price, float) or isinstance(price, int):
                # ✅ Déjà un nombre (Zara) — garder tel quel
                adapter["price"] = float(price)
            elif isinstance(price, str):
                # ✅ Chaine de texte (Jumia, Micromagma) — nettoyer
                price_clean = re.sub(r"[^\d.]", "", price.replace(",", ""))
                try:
                    adapter["price"] = float(price_clean)
                except ValueError:
                    adapter["price"] = None

        # ✅ Nettoyer le nom
        name = adapter.get("name", "")
        if name:
            adapter["name"] = " ".join(name.split())

        # ✅ Ajouter le timestamp si absent
        if not adapter.get("timestamp"):
            adapter["timestamp"] = datetime.utcnow().isoformat()

        return item