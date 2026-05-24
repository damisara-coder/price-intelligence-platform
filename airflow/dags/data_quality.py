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

def check_row_counts():
    base_path = '/opt/airflow/dags/data'
    files = {
        'marjane': 'marjane.json',
        'jumia': 'jumia_clean.json',
        'micromagma': 'micromagma_2026-03-30T21-48-05+00-00.json',
        'zara': 'zara_2026-03-31T10-08-12+00-00.json'
    }

    print("📊 Row Count Check:")
    total = 0
    for source, filename in files.items():
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            count = len(products)
            total += count
            if count == 0:
                raise ValueError(f"❌ {source}: 0 produits trouvés!")
            print(f"  ✅ {source}: {count} produits")
        else:
            raise FileNotFoundError(f"❌ Fichier manquant: {filename}")

    print(f"\n  📦 Total: {total} produits")
    print("✅ Row count check passed!")

def check_null_prices():
    base_path = '/opt/airflow/dags/data'
    files = {
        'marjane': 'marjane.json',
        'jumia': 'jumia_clean.json',
        'micromagma': 'micromagma_2026-03-30T21-48-05+00-00.json',
        'zara': 'zara_2026-03-31T10-08-12+00-00.json'
    }

    print("🔍 Null Price Check:")
    for source, filename in files.items():
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                products = json.load(f)

            null_prices = [p for p in products if not p.get('price')]
            null_count = len(null_prices)
            total = len(products)
            pct = (null_count / total * 100) if total > 0 else 0

            if pct > 20:
                raise ValueError(f"❌ {source}: {pct:.1f}% prix manquants (seuil: 20%)")
            
            print(f"  ✅ {source}: {null_count}/{total} prix manquants ({pct:.1f}%)")

    print("✅ Null price check passed!")

def check_price_validity():
    base_path = '/opt/airflow/dags/data'
    files = {
        'marjane': 'marjane.json',
        'jumia': 'jumia_clean.json',
        'micromagma': 'micromagma_2026-03-30T21-48-05+00-00.json',
        'zara': 'zara_2026-03-31T10-08-12+00-00.json'
    }

    print("💰 Price Validity Check:")
    for source, filename in files.items():
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                products = json.load(f)

            invalid = 0
            for p in products:
                try:
                    price = float(str(p.get('price', 0)).replace(',', '.').replace(' ', ''))
                    if price < 0:
                        invalid += 1
                except:
                    invalid += 1

            print(f"  ✅ {source}: {invalid} prix invalides")

    print("✅ Price validity check passed!")

with DAG(
    dag_id='data_quality_checks',
    default_args=default_args,
    description='Data quality: row counts and null checks',
    schedule_interval='@daily',
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=['quality', 'validation'],
) as dag:

    row_count = PythonOperator(
        task_id='check_row_counts',
        python_callable=check_row_counts,
    )

    null_check = PythonOperator(
        task_id='check_null_prices',
        python_callable=check_null_prices,
    )

    price_validity = PythonOperator(
        task_id='check_price_validity',
        python_callable=check_price_validity,
    )

    row_count >> null_check >> price_validity