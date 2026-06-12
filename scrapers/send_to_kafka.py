from kafka import KafkaProducer
import json
import os
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Liste de toutes les plateformes avec leurs vrais noms de fichiers
platforms = {
    'jumia': 'jumia_clean.json',
    'marjane': 'marjane.json',
    'micromagma': 'micromagma_2026-03-30T21-48-05+00-00.json',
    'zara': 'zara_2026-03-31T10-08-12+00-00.json'
}

for platform, filename in platforms.items():
    path = os.path.join(os.path.dirname(__file__), 'data', filename)

    if not os.path.exists(path):
        print(f"⚠️ Fichier {filename} non trouvé pour {platform}")
        continue

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📦 Envoi des produits de {platform.upper()}...")

    # S'assurer que data est une liste
    if isinstance(data, dict):
        # Si c'est un dictionnaire, essayer de trouver la clé qui contient la liste
        if 'products' in data:
            products = data['products']
        elif 'data' in data:
            products = data['data']
        else:
            products = [data]  # Si c'est un seul produit
    else:
        products = data

    for product in products[:20]:  # Envoyer les 20 premiers produits
        message = {
            'produit': product.get('name', product.get('produit', 'Inconnu')),
            'prix': product.get('price', product.get('prix', 0)),
            'plateforme': platform,
            'categorie': product.get('category', product.get('categorie', 'general')),
            'timestamp': time.time()
        }
        producer.send('prices', message)
        print(f"   ✅ {message['produit'][:50]}... - {message['prix']} MAD")
        time.sleep(0.05)

producer.flush()
print("\n🎉 Tous les produits ont été envoyés !")
