from kafka import KafkaConsumer
import json
import pandas as pd
import os
from datetime import datetime
import time

# ============================================================
# CONFIGURATION
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CSV_FILE = os.path.join(DATA_DIR, 'cleaned_prices.csv')
ALERTS_FILE = os.path.join(DATA_DIR, 'price_alerts.csv')
HISTORY_FILE = os.path.join(DATA_DIR, 'price_history.csv')

# ============================================================
# FONCTIONS POUR LES FICHIERS CSV
# ============================================================


def init_csv_files():
    """Initialise les fichiers CSV s'ils n'existent pas"""

    # Fichier principal des prix
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['name', 'price', 'category', 'source', 'scraped_at'])
        df.to_csv(CSV_FILE, index=False)
        print(f"✅ Fichier créé: {CSV_FILE}")

    # Fichier des alertes
    if not os.path.exists(ALERTS_FILE):
        df = pd.DataFrame(columns=['produit', 'plateforme', 'categorie', 'avant', 'apres', 'baisse', 'economie', 'date'])
        df.to_csv(ALERTS_FILE, index=False)
        print(f"✅ Fichier créé: {ALERTS_FILE}")

    # Fichier historique
    if not os.path.exists(HISTORY_FILE):
        df = pd.DataFrame(columns=['produit', 'prix', 'plateforme', 'categorie', 'timestamp', 'date'])
        df.to_csv(HISTORY_FILE, index=False)
        print(f"✅ Fichier créé: {HISTORY_FILE}")


def save_to_csv(data):
    """Sauvegarde un message dans le fichier CSV principal"""
    try:
        # Lire le fichier existant
        if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
            df = pd.read_csv(CSV_FILE)
        else:
            df = pd.DataFrame(columns=['name', 'price', 'category', 'source', 'scraped_at'])

        # Ajouter le nouveau produit
        new_row = pd.DataFrame([{
            'name': str(data.get('produit', 'Inconnu')),
            'price': float(data.get('prix', 0)),
            'category': str(data.get('categorie', 'general')),
            'source': str(data.get('plateforme', 'unknown')),
            'scraped_at': datetime.now().isoformat()
        }])

        df = pd.concat([df, new_row], ignore_index=True)

        # Supprimer les doublons (garder le plus récent)
        df = df.drop_duplicates(subset=['name', 'source'], keep='last')

        # Sauvegarder
        df.to_csv(CSV_FILE, index=False)
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde CSV: {e}")
        return False


def save_to_history(data):
    """Sauvegarde l'historique des prix pour analyse temporelle"""
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

        # Garder seulement les 10000 derniers enregistrements
        if len(df) > 10000:
            df = df.tail(10000)

        df.to_csv(HISTORY_FILE, index=False)
        return True
    except Exception as e:
        print(f"❌ Erreur historique: {e}")
        return False


def detect_price_drop(product_name, platform, current_price):
    """Détecte une baisse de prix par rapport à l'historique - VERSION CORRIGEE"""
    try:
        if not os.path.exists(HISTORY_FILE):
            return None

        if os.path.getsize(HISTORY_FILE) == 0:
            return None

        df = pd.read_csv(HISTORY_FILE)

        # Vérifier que les colonnes existent
        if 'prix' not in df.columns or 'produit' not in df.columns:
            return None

        # Convertir les prix en numérique
        df['prix'] = pd.to_numeric(df['prix'], errors='coerce')

        # Convertir le prix actuel en float
        try:
            current_price = float(current_price)
        except (ValueError, TypeError):
            return None

        # Filtrer par produit et plateforme
        product_history = df[(df['produit'].astype(str) == str(product_name)) &
                             (df['plateforme'].astype(str) == str(platform))]

        if len(product_history) < 2:
            return None

        # Obtenir le prix précédent
        previous_price = None
        for idx in range(len(product_history) - 2, -1, -1):
            try:
                prev = float(product_history.iloc[idx]['prix'])
                if prev > 0:
                    previous_price = prev
                    break
            except BaseException:
                continue

        if previous_price is None:
            return None

        # Vérifier la baisse
        if previous_price > current_price and previous_price > 0:
            baisse_pct = round((previous_price - current_price) / previous_price * 100, 1)
            if baisse_pct >= 10:  # Alerte si baisse > 10%
                # Récupérer la catégorie
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
    except Exception as e:
        # Ne pas afficher d'erreur pour ne pas polluer la console
        return None


def save_alert(alert):
    """Sauvegarde une alerte dans le fichier des alertes"""
    try:
        if alert is None:
            return False

        if os.path.exists(ALERTS_FILE) and os.path.getsize(ALERTS_FILE) > 0:
            df = pd.read_csv(ALERTS_FILE)
        else:
            df = pd.DataFrame(columns=['produit', 'plateforme', 'categorie', 'avant', 'apres', 'baisse', 'economie', 'date'])

        new_row = pd.DataFrame([alert])
        df = pd.concat([df, new_row], ignore_index=True)

        # Garder seulement les 1000 dernières alertes
        if len(df) > 1000:
            df = df.tail(1000)

        df.to_csv(ALERTS_FILE, index=False)
        print(f"🔔 ALERTE: {alert['produit']} a baissé de {alert['baisse']}% ({alert['avant']} -> {alert['apres']} MAD)")
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde alerte: {e}")
        return False


def update_summary_stats():
    """Met à jour les statistiques résumées dans un fichier CSV"""
    try:
        if not os.path.exists(CSV_FILE):
            return

        if os.path.getsize(CSV_FILE) == 0:
            return

        df = pd.read_csv(CSV_FILE)

        # S'assurer que les prix sont numériques
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price'])

        if len(df) == 0:
            return

        # Calculer les statistiques par catégorie et plateforme
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

        # Sauvegarder
        stats_file = os.path.join(DATA_DIR, 'clean_summary_stats.csv')
        stats.to_csv(stats_file, index=False)

        # Aussi sauvegarder les stats par marque (si disponible)
        if 'brand' in df.columns:
            brand_stats = df.groupby(['brand', 'category']).agg({
                'price': ['mean', 'median', 'min', 'max', 'count']
            }).round(2)
            brand_stats.columns = ['mean_price', 'median_price', 'min_price', 'max_price', 'product_count']
            brand_stats = brand_stats.reset_index()
            brand_stats.to_csv(os.path.join(DATA_DIR, 'brand_stats.csv'), index=False)

        return True
    except Exception as e:
        print(f"❌ Erreur mise à jour stats: {e}")
        return False

# ============================================================
# CONSUMER KAFKA
# ============================================================


def start_consumer():
    """Démarre le consumer Kafka"""

    # Initialiser les fichiers CSV
    init_csv_files()

    # Configuration du consumer
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
    print("=" * 60)

    message_count = 0
    last_stats_update = time.time()

    try:
        for message in consumer:
            data = message.value
            message_count += 1

            # Sauvegarder dans le fichier principal
            if save_to_csv(data):
                print(f"✅ [{message_count}] {str(data.get('produit', 'Inconnu'))[:40]}... - {data.get('prix', 0)} MAD")

            # Sauvegarder dans l'historique
            save_to_history(data)

            # Détecter les baisses de prix
            alert = detect_price_drop(
                data.get('produit', 'Inconnu'),
                data.get('plateforme', 'unknown'),
                data.get('prix', 0)
            )
            if alert:
                save_alert(alert)

            # Mettre à jour les stats toutes les 10 secondes
            if time.time() - last_stats_update > 10:
                update_summary_stats()
                last_stats_update = time.time()
                print(f"📊 Statistiques mises à jour - Total produits: {message_count}")

    except KeyboardInterrupt:
        print("\n🛑 Consumer arrêté par l'utilisateur")

        print("📊 Mise à jour des statistiques finales...")
        update_summary_stats()
    finally:
        consumer.close()
        print("👋 Consumer fermé")


# ============================================================
# LANCEMENT
# ============================================================
if __name__ == "__main__":
    start_consumer()
