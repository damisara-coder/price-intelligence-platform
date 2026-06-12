from kafka import KafkaConsumer
import json
import pandas as pd
import os
from datetime import datetime
import time
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

# ============================================================
# CONFIGURATION
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CSV_FILE = os.path.join(DATA_DIR, 'cleaned_prices.csv')
ALERTS_FILE = os.path.join(DATA_DIR, 'price_alerts.csv')
HISTORY_FILE = os.path.join(DATA_DIR, 'price_history.csv')

# Configuration BigQuery (CORRIGÉ avec les bonnes valeurs)
PROJECT_ID = "bionic-baton-496415-h5"
DATASET_ID = "ecommerce_prices"
TABLE_ID = "cleaned_prices"
BIGQUERY_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Initialiser BigQuery client
try:
    bigquery_client = bigquery.Client(project=PROJECT_ID)
    print(f"✅ Connexion BigQuery établie pour {PROJECT_ID}")
    print(f"📤 Table cible: {BIGQUERY_TABLE}")
except Exception as e:
    print(f"⚠️ Erreur BigQuery: {e}")
    bigquery_client = None

# ============================================================
# FONCTIONS POUR LES FICHIERS CSV
# ============================================================


def init_csv_files():
    """Initialise les fichiers CSV s'ils n'existent pas"""

    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['name', 'price', 'category', 'source', 'scraped_at'])
        df.to_csv(CSV_FILE, index=False)
        print(f"✅ Fichier créé: {CSV_FILE}")

    if not os.path.exists(ALERTS_FILE):
        df = pd.DataFrame(columns=['produit', 'plateforme', 'categorie', 'avant', 'apres', 'baisse', 'economie', 'date'])
        df.to_csv(ALERTS_FILE, index=False)
        print(f"✅ Fichier créé: {ALERTS_FILE}")

    if not os.path.exists(HISTORY_FILE):
        df = pd.DataFrame(columns=['produit', 'prix', 'plateforme', 'categorie', 'timestamp', 'date'])
        df.to_csv(HISTORY_FILE, index=False)
        print(f"✅ Fichier créé: {HISTORY_FILE}")


def save_to_csv(data):
    """Sauvegarde un message dans le fichier CSV principal"""
    try:
        if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
            df = pd.read_csv(CSV_FILE)
        else:
            df = pd.DataFrame(columns=['name', 'price', 'category', 'source', 'scraped_at'])

        new_row = pd.DataFrame([{
            'name': str(data.get('produit', 'Inconnu')),
            'price': float(data.get('prix', 0)),
            'category': str(data.get('categorie', 'general')),
            'source': str(data.get('plateforme', 'unknown')),
            'scraped_at': datetime.now().isoformat()
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        df = df.drop_duplicates(subset=['name', 'source'], keep='last')
        df.to_csv(CSV_FILE, index=False)
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde CSV: {e}")
        return False


def save_to_history(data):
    """Sauvegarde l'historique des prix"""
    try:
        if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
            df = pd.read_csv(HISTORY_FILE)
        else:
            df = pd.DataFrame(columns=['produit', 'prix', 'plateforme', 'categorie', 'timestamp', 'date'])

        new_row = pd.DataFrame([{
            'produit': str(data.get('produit', 'Inconnu')),
            'prix': float(data.get('prix', 0)),
            'plateforme': str(data.get('plateforme', 'unknown')),
            'categorie': str(data.get('categorie', 'general')),
            'timestamp': float(data.get('timestamp', time.time())),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        if len(df) > 10000:
            df = df.tail(10000)
        df.to_csv(HISTORY_FILE, index=False)
        return True
    except Exception as e:
        print(f"❌ Erreur historique: {e}")
        return False

# ============================================================
# FONCTION BIGQUERY CORRIGÉE (ADAPTÉE AU SCHEMA EXISTANT)
# ============================================================


def save_to_bigquery(data):
    """Envoie un message vers BigQuery - adapté au schema existant"""
    if bigquery_client is None:
        return False

    try:
        # Adapter les noms de colonnes à ceux de la table BigQuery existante
        now = datetime.now()
        rows_to_insert = [{
            'product_name': str(data.get('produit', 'Inconnu')),
            'price_mad': float(data.get('prix', 0)),
            'source_platform': str(data.get('plateforme', 'unknown')),
            'category_normalized': str(data.get('categorie', 'general')),
            'category_raw': str(data.get('categorie', 'general')),
            'scraped_at_ts': now.isoformat(),
            'ingested_at_ts': now.isoformat(),
            'price_date': now.date().isoformat(),
            'price_hour': now.hour,
            'is_price_outlier': False,
            'price_segment': 'standard'
        }]

        errors = bigquery_client.insert_rows_json(BIGQUERY_TABLE, rows_to_insert)

        if not errors:
            print(f"📤 BigQuery: {data.get('produit')[:40]}... - {data.get('prix')} MAD")
            return True
        else:
            print(f"⚠️ Erreur BigQuery: {errors}")
            return False
    except Exception as e:
        print(f"⚠️ Exception BigQuery: {e}")
        return False


def detect_price_drop(product_name, platform, current_price):
    """Détecte une baisse de prix"""
    try:
        if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
            return None

        df = pd.read_csv(HISTORY_FILE)

        if 'prix' not in df.columns or 'produit' not in df.columns:
            return None

        df['prix'] = pd.to_numeric(df['prix'], errors='coerce')
        current_price = float(current_price)

        product_history = df[(df['produit'].astype(str) == str(product_name)) &
                             (df['plateforme'].astype(str) == str(platform))]

        if len(product_history) < 2:
            return None

        previous_price = None
        for idx in range(len(product_history) - 2, -1, -1):
            try:
                prev = float(product_history.iloc[idx]['prix'])
                if prev > 0:
                    previous_price = prev
                    break
            except BaseException:
                continue

        if previous_price is None or previous_price <= current_price:
            return None

        baisse_pct = round((previous_price - current_price) / previous_price * 100, 1)
        if baisse_pct >= 10:
            categorie = 'general'
            if 'categorie' in product_history.columns:
                categorie = str(product_history.iloc[-2].get('categorie', 'general'))

            return {
                'produit': str(product_name),
                'plateforme': str(platform),
                'categorie': categorie,
                'avant': int(previous_price),
                'apres': int(current_price),
                'baisse': baisse_pct,
                'economie': int(previous_price - current_price),
                'date': datetime.now().isoformat()
            }
        return None
    except Exception:
        return None


def save_alert(alert):
    """Sauvegarde une alerte"""
    if alert is None:
        return False

    try:
        if os.path.exists(ALERTS_FILE) and os.path.getsize(ALERTS_FILE) > 0:
            df = pd.read_csv(ALERTS_FILE)
        else:
            df = pd.DataFrame(columns=['produit', 'plateforme', 'categorie', 'avant', 'apres', 'baisse', 'economie', 'date'])

        new_row = pd.DataFrame([alert])
        df = pd.concat([df, new_row], ignore_index=True)

        if len(df) > 1000:
            df = df.tail(1000)

        df.to_csv(ALERTS_FILE, index=False)
        print(f"🔔 ALERTE: {alert['produit']} a baissé de {alert['baisse']}%")
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde alerte: {e}")
        return False


def update_summary_stats():
    """Met à jour les statistiques résumées"""
    try:
        if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
            return

        df = pd.read_csv(CSV_FILE)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price'])

        if len(df) == 0:
            return

        stats = df.groupby(['category', 'source']).agg({
            'price': ['mean', 'median', 'min', 'max', 'std', 'count']
        }).round(2)

        stats.columns = ['mean_price', 'median_price', 'min_price', 'max_price', 'std_price', 'count']
        stats = stats.reset_index()
        stats.columns = [
            'category_normalized',
            'source_platform',
            'mean_price',
            'median_price',
            'min_price',
            'max_price',
            'std_price',
            'count']

        stats_file = os.path.join(DATA_DIR, 'clean_summary_stats.csv')
        stats.to_csv(stats_file, index=False)
        return True
    except Exception as e:
        print(f"❌ Erreur mise à jour stats: {e}")
        return False

# ============================================================
# CONSUMER KAFKA
# ============================================================


def start_consumer():
    """Démarre le consumer Kafka"""

    init_csv_files()

    consumer = KafkaConsumer(
        'prices',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='price-consumer-group-csv',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("=" * 60)
    print("🟢 CONSUMER KAFKA DÉMARRÉ")
    print("📡 Connecté à localhost:9092")
    print("📦 Topic: prices")
    print("💾 Sauvegarde vers: CSV files")
    if bigquery_client:
        print(f"📤 Envoi vers: BigQuery ({BIGQUERY_TABLE})")
    else:
        print("⚠️ BigQuery non configuré")
    print("=" * 60)

    message_count = 0
    last_stats_update = time.time()

    try:
        for message in consumer:
            data = message.value
            message_count += 1

            # Sauvegarder dans CSV
            if save_to_csv(data):
                print(f"✅ [{message_count}] {str(data.get('produit', 'Inconnu'))[:40]}... - {data.get('prix', 0)} MAD")

            # Sauvegarder dans l'historique
            save_to_history(data)

            # Envoyer vers BigQuery
            if bigquery_client:
                save_to_bigquery(data)

            # Détecter les alertes
            alert = detect_price_drop(
                data.get('produit', 'Inconnu'),
                data.get('plateforme', 'unknown'),
                data.get('prix', 0)
            )
            if alert:
                save_alert(alert)

            # Mettre à jour les stats
            if time.time() - last_stats_update > 10:
                update_summary_stats()
                last_stats_update = time.time()
                print(f"📊 Statistiques mises à jour - Total produits: {message_count}")

    except KeyboardInterrupt:
        print("\n🛑 Consumer arrêté")
        update_summary_stats()
    finally:
        consumer.close()
        print("👋 Consumer fermé")


# ============================================================
# LANCEMENT
# ============================================================
if __name__ == "__main__":
    start_consumer()
