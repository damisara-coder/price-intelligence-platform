SELECT
    source_label,
    category,
    COUNT(*)        AS nb_produits,
    ROUND(AVG(price), 2)  AS prix_moyen,
    ROUND(MIN(price), 2)  AS prix_min,
    ROUND(MAX(price), 2)  AS prix_max,
    ROUND(STDDEV(price), 2) AS ecart_type
FROM {{ ref('cleaned_products') }}
GROUP BY source_label, category
ORDER BY category, source_label