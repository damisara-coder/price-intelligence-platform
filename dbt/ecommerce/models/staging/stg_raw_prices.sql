-- =============================================================
-- MODEL: stg_raw_prices
-- Layer: Staging
-- Description: Nettoie les types, renomme les colonnes,
--              génère un row_key unique depuis les données brutes.
-- Source: BigQuery table `raw_prices` (chargée depuis scrapers)
-- =============================================================

WITH source_data AS (

    SELECT *
    FROM {{ source('ecommerce_raw', 'products') }}

),

renamed AS (

    SELECT

        -- Clé unique
        TO_HEX(
            MD5(
                CONCAT(
                    COALESCE(url, ''),
                    '#',
                    COALESCE(CAST(timestamp AS STRING), '')
                )
            )
        ) AS row_key,

        -- Colonnes nettoyées
        TRIM(name) AS product_name,

        CAST(price AS FLOAT64) AS price_mad,

        LOWER(TRIM(category)) AS category,

        LOWER(TRIM(source)) AS source_platform,

        TRIM(url) AS product_url,

        -- Dates
        CAST(timestamp AS TIMESTAMP) AS scraped_at_ts,

        CAST(scraped_at AS TIMESTAMP) AS ingested_at_ts,

        DATE(CAST(timestamp AS TIMESTAMP)) AS price_date,

        EXTRACT(HOUR FROM CAST(timestamp AS TIMESTAMP)) AS price_hour

    FROM source_data

    WHERE
        url IS NOT NULL
        AND name IS NOT NULL
        AND price IS NOT NULL

)

SELECT *
FROM renamed