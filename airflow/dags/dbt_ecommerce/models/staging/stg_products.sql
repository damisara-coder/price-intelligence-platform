SELECT
    name,
    CAST(price AS FLOAT64) AS price,
    category,
    source,
    url,
    CAST(timestamp AS TIMESTAMP) AS scraped_at
FROM `bionic-baton-496415-h5.ecommerce_prices.products`
WHERE price IS NOT NULL
  AND name IS NOT NULL