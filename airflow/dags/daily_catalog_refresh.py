from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from kafka import KafkaProducer
import json
import os

default_args = {
    'owner': 'data-engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def send_to_kafka():
    producer = KafkaProducer(
        bootstrap_servers=['kafka:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    base_path = '/opt/airflow/dags/data'
    files = {
        'marjane': 'marjane.json',
        'jumia': 'jumia_clean.json',
        'micromagma': 'micromagma_2026-03-30T21-48-05+00-00.json',
        'zara': 'zara_2026-03-31T10-08-12+00-00.json'
    }
    
    total = 0
    for source, filename in files.items():
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            for product in products:
                product['source'] = source
                producer.send('ecommerce-prices', value=product)
                total += 1
            print(f"✅ {source}: {len(products)} produits envoyés")
    
    producer.flush()
    print(f"🎉 Total: {total} produits envoyés vers Kafka!")

with DAG(
    dag_id='daily_catalog_refresh',
    default_args=default_args,
    description='Daily scraper → Kafka pipeline',
    schedule_interval='@daily',
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=['scraper', 'kafka'],
) as dag:

    send_data = PythonOperator(
        task_id='send_scraped_data_to_kafka',
        python_callable=send_to_kafka,
    )