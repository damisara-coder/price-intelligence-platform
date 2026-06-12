import json
import requests
import os

path = r"C:\Users\hp\Desktop\price-intelligence-platform\scrapers\data\\"

files = [
    'all_products.json',
    'jumia_clean.json',
    'marjane.json',
    'dynamic_2026-03-31T10-38-53+00-00.json',
    'micromagma_2026-03-30T21-48-05+00-00.json',
    'zara_2026-03-31T10-08-12+00-00.json'
]

all_products = []
for file in files:
    filepath = path + file
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            products = json.load(f)
            all_products.extend(products)
            print(f"✅ {file}: {len(products)} produits")

# Supprimer doublons par URL
seen = set()
unique_products = []
for p in all_products:
    url = p.get('url', '')
    if url and url not in seen:
        seen.add(url)
        unique_products.append(p)

print(f"\nTotal unique: {len(unique_products)} produits")

# Envoyer vers NiFi
success = 0
for product in unique_products:
    response = requests.post(
        'http://localhost:9999/contentListener',
        json=product,
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code == 200:
        success += 1

print(f"🎉 {success}/{len(unique_products)} produits envoyés vers NiFi !")
