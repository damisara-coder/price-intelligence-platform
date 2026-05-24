-- =============================================================
-- TEST CUSTOM: assert_no_duplicate_daily_product
-- Description:
-- Vérifie qu'il n'existe pas de doublons
-- pour le même produit / même plateforme / même jour.
-- Le test doit retourner 0 lignes pour PASS.
-- =============================================================

WITH counts AS (

    SELECT
        product_url,
        price_date,
        source_platform,
        COUNT(*) AS cnt

    FROM {{ ref('agg_daily_prices') }}

    GROUP BY
        product_url,
        price_date,
        source_platform
)

SELECT *
FROM counts
WHERE cnt > 1