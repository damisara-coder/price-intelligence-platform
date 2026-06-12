-- =============================================================
-- TEST CUSTOM: assert_price_in_valid_range
-- Description:
-- Vérifie qu'aucun prix dans cleaned_prices
-- n'est <= 0 ou > 100000 MAD.
-- Le test doit retourner 0 lignes pour PASS.
-- =============================================================

SELECT
    row_key,
    product_name,
    price_mad,
    source_platform,
    price_date

FROM {{ ref('cleaned_prices') }}

WHERE price_mad <= 0
   OR price_mad > 100000