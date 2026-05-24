-- =============================================================
-- MODEL: agg_daily_prices
-- Layer: Aggregated
-- =============================================================

WITH cleaned AS (

    SELECT *
    FROM {{ ref('cleaned_prices') }}

),

daily_stats AS (

    SELECT

        price_date,
        source_platform,
        category_normalized,
        brand,
        price_segment,
        product_url,
        product_name,

        COUNT(*) AS observation_count,

        ROUND(AVG(price_mad), 2) AS avg_price_mad,
        ROUND(MIN(price_mad), 2) AS min_price_mad,
        ROUND(MAX(price_mad), 2) AS max_price_mad,

        ROUND(STDDEV(price_mad), 2) AS std_price_mad,

        ARRAY_AGG(
            price_mad
            ORDER BY scraped_at_ts ASC
            LIMIT 1
        )[OFFSET(0)] AS open_price_mad,

        ARRAY_AGG(
            price_mad
            ORDER BY scraped_at_ts DESC
            LIMIT 1
        )[OFFSET(0)] AS close_price_mad

    FROM cleaned

    GROUP BY
        price_date,
        source_platform,
        category_normalized,
        brand,
        price_segment,
        product_url,
        product_name

),

with_velocity AS (

    SELECT

        *,

        LAG(close_price_mad) OVER (
            PARTITION BY product_url
            ORDER BY price_date
        ) AS prev_day_price,

        ROUND(
            SAFE_DIVIDE(
                close_price_mad -
                LAG(close_price_mad) OVER (
                    PARTITION BY product_url
                    ORDER BY price_date
                ),
                NULLIF(
                    LAG(close_price_mad) OVER (
                        PARTITION BY product_url
                        ORDER BY price_date
                    ),
                    0
                )
            ) * 100,
            2
        ) AS price_change_pct,

        ROUND(
            AVG(avg_price_mad) OVER (
                PARTITION BY product_url
                ORDER BY price_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ),
            2
        ) AS moving_avg_7d

    FROM daily_stats

)

SELECT

    TO_HEX(MD5(CONCAT(
        CAST(price_date AS STRING),
        '#',
        source_platform,
        '#',
        product_url
    ))) AS agg_row_key,

    price_date,
    source_platform,
    category_normalized,
    brand,
    price_segment,
    product_url,
    product_name,
    observation_count,
    avg_price_mad,
    min_price_mad,
    max_price_mad,
    std_price_mad,
    open_price_mad,
    close_price_mad,
    prev_day_price,
    price_change_pct,
    moving_avg_7d,

    CASE
        WHEN ABS(price_change_pct) > 10 THEN TRUE
        ELSE FALSE
    END AS is_price_alert

FROM with_velocity