from google.cloud import bigquery

client = bigquery.Client()
print("✅ Connexion réussie !")

# Tester la requête
query = "SELECT 1 as test"
result = client.query(query).to_dataframe()
print(result)

# Vérifier si la table existe
dataset_ref = client.dataset("price_data")
table_ref = dataset_ref.table("prices")

try:
    client.get_table(table_ref)
    print("✅ La table prices existe !")
except Exception as e:
    print(f"❌ La table n'existe pas: {e}")