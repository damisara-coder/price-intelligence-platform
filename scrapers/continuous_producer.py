from kafka import KafkaProducer
import json
import os
import time
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Liste des fichiers JSON pour chaque plateforme
platforms_files = {
    'jumia': 'jumia_clean.json',
    'marjane': 'marjane.json',
    'micromagma': 'micromagma_2026-03-30T21-48-05+00-00.json',
    'zara': 'zara_2026-03-31T10-08-12+00-00.json'
}

print("🟢 PRODUCER CONTINU DÉMARRÉ")
print("📡 Envoi de messages à Kafka toutes les 10 secondes")
print("=" * 50)

while True:
    for platform, filename in platforms_files.items():
        path = os.path.join(os.path.dirname(__file__), 'data', filename)
        
        if not os.path.exists(path):
            print(f"⚠️ Fichier {filename} non trouvé pour {platform}")
            continue
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Gérer différents formats de JSON
        if isinstance(data, dict):
            products = data.get('products', data.get('data', []))
        else:
            products = data
        
        if products and len(products) > 0:
            # Envoyer 3 produits aléatoires à chaque cycle
            sample_size = min(3, len(products))
            for product in random.sample(products, sample_size):
                # Récupérer le prix et ajouter une variation de -5% à +5%
                original_price = product.get('price', product.get('prix', 0))
                if isinstance(original_price, str):
                    original_price = float(original_price.replace('MAD', '').strip())
                
                price_variation = original_price * random.uniform(0.95, 1.05)
                
                message = {
                    'produit': product.get('name', product.get('produit', 'Inconnu')),
                    'prix': round(price_variation, 2),
                    'plateforme': platform,
                    'categorie': product.get('category', product.get('categorie', 'general')),
                    'timestamp': time.time()
                }
                producer.send('prices', message)
                print(f"📤 [{platform}] {message['produit'][:35]}... - {message['prix']} MAD")
    
    print(f"⏱️ Attente 10 secondes...")
    time.sleep(10)