from kafka import KafkaProducer
import json
import os

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

base_path = r"C:\Users\hp\Desktop\price-intelligence-platform\scrapers\data"

files = {
    "marjane": "marjane.json",
    "jumia": "jumia_clean.json",
    "micromagma": "micromagma_2026-03-30T21-48-05+00-00.json",
    "zara": "zara_2026-03-31T10-08-12+00-00.json"
}

total = 0
for source, filename in files.items():
    path = os.path.join(base_path, filename)
    with open(path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    for product in products:
        product['source'] = source
        producer.send('ecommerce-prices', value=product)
        total += 1
    print(f"✅ {source}: {len(products)} produits envoyés")

producer.flush()
print(f"\n🎉 Total: {total} produits envoyés vers Kafka!")