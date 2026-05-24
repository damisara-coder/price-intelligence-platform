# 📊 dbt Project — Price Intelligence Platform
**Data Analyst** | Pr. ELAACHAK | Data Engineering & Analytics 2025-2026

---

## Architecture des modèles dbt

```
BigQuery (raw.raw_prices)
        │
        ▼
┌─────────────────────────────┐
│  STAGING: stg_raw_prices    │  ← Vue légère, types nettoyés, row_key généré
│  Matérialisation: VIEW      │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  CLEANED: cleaned_prices    │  ← Déduplication, normalisation, marques, segments
│  Matérialisation: TABLE     │
└──────────┬──────────────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌──────────────┐  ┌─────────────────────────┐
│ agg_daily_   │  │ agg_weekly_category_    │
│ prices       │  │ stats                   │
│              │  │                         │
│ Grain: url   │  │ Grain: catégorie ×      │
│ × plateforme │  │ plateforme × semaine    │
│ × jour       │  │                         │
└──────────────┘  └─────────────────────────┘
        │
        ▼
  Dashboard Streamlit
  Notebooks Python
```

## Modèles

| Modèle | Couche | Grain | Lignes (estimé) | Description |
|--------|--------|-------|-----------------|-------------|
| `stg_raw_prices` | Staging | 1 observation brute | ~6000 | Types, row_key |
| `cleaned_prices` | Cleaned | 1 observation unique | ~3000 | Dedup, normalisation |
| `agg_daily_prices` | Aggregated | produit × jour × plateforme | ~variable | Vélocité, alertes |
| `agg_weekly_category_stats` | Aggregated | catégorie × semaine × plateforme | ~variable | Stats hebdo |

## Tests dbt

```bash
# Lancer tous les tests
dbt test

# Tests sur un modèle spécifique
dbt test --select cleaned_prices
dbt test --select agg_daily_prices

# Tests custom
dbt test --select test_type:singular
```

### Tests configurés

| Test | Modèle | Type |
|------|--------|------|
| `not_null` sur `row_key` | tous | generic |
| `unique` sur `row_key` | tous | generic |
| `accepted_values` sur `source_platform` | staging, cleaned | generic |
| `accepted_values` sur `category_normalized` | cleaned | generic |
| `accepted_values` sur `price_segment` | cleaned | generic |
| `assert_price_in_valid_range` | cleaned | singular |
| `assert_no_duplicate_daily_product` | aggregated | singular |

## Commandes utiles

```bash
# Compiler les modèles
dbt compile

# Exécuter tous les modèles
dbt run

# Exécuter par couche
dbt run --select staging
dbt run --select cleaned
dbt run --select aggregated

# Générer la documentation
dbt docs generate
dbt docs serve   # Ouvre http://localhost:8080

# Rafraîchissement incrémental (si configuré)
dbt run --select agg_daily_prices --full-refresh
```

## Variables d'environnement requises

```bash
export DBT_BIGQUERY_PROJECT="your-gcp-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## Profil BigQuery (~/.dbt/profiles.yml)

```yaml
ecommerce_bigquery:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: "{{ env_var('DBT_BIGQUERY_PROJECT') }}"
      dataset: ecommerce_dev
      keyfile: "{{ env_var('GOOGLE_APPLICATION_CREDENTIALS') }}"
      location: EU
      threads: 4
      timeout_seconds: 300
    prod:
      type: bigquery
      method: service-account
      project: "{{ env_var('DBT_BIGQUERY_PROJECT') }}"
      dataset: ecommerce_prod
      keyfile: "{{ env_var('GOOGLE_APPLICATION_CREDENTIALS') }}"
      location: EU
      threads: 8
      timeout_seconds: 600
```

## Lineage Graph

```
raw_prices (source)
    └── stg_raw_prices (staging/view)
            └── cleaned_prices (cleaned/table)
                    ├── agg_daily_prices (aggregated/table)
                    └── agg_weekly_category_stats (aggregated/table)
```

## Notebooks Python (analyses statistiques)

| Notebook | Contenu |
|----------|---------|
| `01_descriptive_stats.ipynb` | Moyenne, médiane, std, histogrammes, heatmap catégorie × plateforme |
| `02_inferential_stats.ipynb` | t-test (Jumia vs Marjane), ANOVA (catégories), Régression OLS, IC 95% |
| `03_export_csv.ipynb` | Génère les 4 CSV pour le dashboard Streamlit |

## Exports CSV (pour Full Stack)

| Fichier | Description |
|---------|-------------|
| `clean_summary_stats.csv` | Stats descriptives par catégorie × plateforme |
| `daily_prices_dashboard.csv` | Prix journaliers pour le graphe Plotly |
| `price_alerts.csv` | Produits avec variation > 10% |
| `brand_stats.csv` | Stats par marque |