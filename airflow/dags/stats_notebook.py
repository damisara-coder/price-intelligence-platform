from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import os

default_args = {
    'owner': 'data-engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def compute_stats():
    base_path = '/opt/airflow/dags/data'
    files = {
        'marjane': 'marjane.json',
        'jumia': 'jumia_clean.json',
        'micromagma': 'micromagma_2026-03-30T21-48-05+00-00.json',
        'zara': 'zara_2026-03-31T10-08-12+00-00.json'
    }

    all_products = []
    for source, filename in files.items():
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            for p in products:
                p['source'] = source
            all_products.extend(products)

    print(f"📦 Total produits chargés: {len(all_products)}")

    # Stats par source
    sources = {}
    for p in all_products:
        source = p.get('source', 'unknown')
        if source not in sources:
            sources[source] = []
        try:
            price = float(str(p.get('price', 0)).replace(',', '.').replace(' ', ''))
            if price > 0:
                sources[source].append(price)
        except:
            pass

    print("\n📊 Stats par site:")
    for source, prices in sources.items():
        if prices:
            print(f"  {source}:")
            print(f"    - Produits: {len(prices)}")
            print(f"    - Prix moyen: {sum(prices)/len(prices):.2f} MAD")
            print(f"    - Prix min: {min(prices):.2f} MAD")
            print(f"    - Prix max: {max(prices):.2f} MAD")

    print("\n🎉 Stats calculées avec succès!")

with DAG(
    dag_id='stats_notebook',
    default_args=default_args,
    description='Compute price statistics from scraped data',
    schedule_interval='@daily',
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=['stats', 'analytics'],
) as dag:

    compute_price_stats = PythonOperator(
        task_id='compute_price_stats',
        python_callable=compute_stats,
    )