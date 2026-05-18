FROM apache/airflow:2.9.0-python3.11

# Switch to root only to install system packages
USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user (required by official Airflow image)
USER airflow

# --- Install extra Python packages ---
# dbt-bigquery: lets Airflow DAGs call dbt models on BigQuery/Bigtable external tables
# apache-airflow-providers-google: gives Airflow the BigtableHook, GCS operators, etc.
# apache-airflow-providers-dbt-cloud: optional but lets you use dbt operators in DAGs
RUN pip install --no-cache-dir \
    dbt-bigquery==1.7.8 \
    apache-airflow-providers-google==10.14.0 \
    apache-airflow-providers-dbt-cloud==3.9.0 \
    google-cloud-bigtable==2.23.0 \
    itemadapter==0.9.0