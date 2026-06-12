{{ config(
    materialized='table'
) }}

-- =============================================================
-- MODEL: cleaned_prices
-- Layer: Cleaned
-- Description:
-- Déduplication, gestion des nulls, normalisation,
-- enrichissement des données.
-- =============================================================

WITH staged AS (

    SELECT *
    FROM {{ ref('stg_raw_prices') }}

),

-- =============================================================
-- Étape 1 : Déduplication
-- Même URL + même timestamp = garder la ligne la plus récente
-- =============================================================

deduped AS (

    SELECT *
    FROM staged

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY product_url, scraped_at_ts
        ORDER BY ingested_at_ts DESC
    ) = 1

),

-- =============================================================
-- Étape 2 : Nettoyage & enrichissement
-- =============================================================

cleaned AS (

    SELECT

        row_key,

        product_name,

        -- =====================================================
        -- Nettoyage du prix
        -- =====================================================

        CASE
            WHEN price_mad <= 0 THEN NULL
            WHEN price_mad > 100000 THEN NULL
            ELSE price_mad
        END AS price_mad,

        -- =====================================================
        -- Catégories normalisées
        -- =====================================================

        CASE

            WHEN category IN (
                'smartphone',
                'smartphones',
                'telephone',
                'telephones',
                'phone'
            )
            THEN 'smartphones'

            WHEN category IN (
                'electromenager',
                'électroménager',
                'home_appliances'
            )
            THEN 'electromenager'

            WHEN category IN (
                'informatique',
                'ordinateur',
                'pc',
                'laptop'
            )
            THEN 'informatique'

            WHEN category IN (
                'vetement',
                'vetements',
                'vêtements',
                'mode',
                'fashion'
            )
            THEN 'mode'

            WHEN category IN (
                'tv',
                'television',
                'télévision',
                'audio_video'
            )
            THEN 'tv_audio'

            ELSE 'other'
            
        END AS category_normalized,

        category AS category_raw,

        source_platform,

        product_url,

        scraped_at_ts,

        ingested_at_ts,

        price_date,

        price_hour,

        -- =====================================================
        -- Flag outlier
        -- =====================================================

        CASE
            WHEN price_mad <= 0 OR price_mad > 100000
            THEN TRUE
            ELSE FALSE
        END AS is_price_outlier,

        -- =====================================================
        -- Détection marque
        -- =====================================================

        CASE

            WHEN LOWER(product_name) LIKE '%samsung%'
                THEN 'Samsung'

            WHEN LOWER(product_name) LIKE '%apple%'
              OR LOWER(product_name) LIKE '%iphone%'
              OR LOWER(product_name) LIKE '%ipad%'
                THEN 'Apple'

            WHEN LOWER(product_name) LIKE '%xiaomi%'
              OR LOWER(product_name) LIKE '%redmi%'
                THEN 'Xiaomi'

            WHEN LOWER(product_name) LIKE '%oppo%'
                THEN 'Oppo'

            WHEN LOWER(product_name) LIKE '%tecno%'
                THEN 'Tecno'

            WHEN LOWER(product_name) LIKE '%itel%'
                THEN 'Itel'

            WHEN LOWER(product_name) LIKE '%huawei%'
                THEN 'Huawei'

            WHEN LOWER(product_name) LIKE '%anker%'
                THEN 'Anker'

            WHEN LOWER(product_name) LIKE '%haylou%'
                THEN 'Haylou'

            WHEN LOWER(product_name) LIKE '%baseus%'
                THEN 'Baseus'

            ELSE 'Other'

        END AS brand,

        -- =====================================================
        -- Segments de prix
        -- =====================================================

        CASE

            WHEN price_mad < 200
                THEN 'budget'

            WHEN price_mad BETWEEN 200 AND 999
                THEN 'entry'

            WHEN price_mad BETWEEN 1000 AND 2999
                THEN 'mid_range'

            WHEN price_mad BETWEEN 3000 AND 7999
                THEN 'high_end'

            WHEN price_mad >= 8000
                THEN 'premium'

            ELSE 'unknown'

        END AS price_segment

    FROM deduped

    WHERE price_mad IS NOT NULL
      AND product_name IS NOT NULL

)

SELECT *
FROM cleaned