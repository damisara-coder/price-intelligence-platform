SELECT
    name,
    price,
    category,
    source,
    url,
    scraped_at,
    CASE
        WHEN source = 'jumia'      THEN 'Jumia Maroc'
        WHEN source = 'micromagma' THEN 'Micromagma'
        WHEN source = 'zara'       THEN 'Zara Maroc'
        ELSE source
    END AS source_label
FROM {{ ref('stg_products') }}
WHERE price > 0
  AND price < 1000000