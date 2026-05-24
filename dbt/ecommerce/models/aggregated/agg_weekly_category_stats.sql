-- =============================================================
-- MODEL: agg_weekly_category_stats
-- Layer: Aggregated
-- =============================================================

WITH cleaned AS (

    SELECT *
    FROM {{ ref('cleaned_prices') }}

),

weekly_base AS (

    SELECT

        DATE_TRUNC(price_date, WEEK(MONDAY)) AS week_start,

        EXTRACT(YEAR FROM price_date) AS year_num,
        EXTRACT(WEEK FROM price_date) AS week_num,

        source_platform,
        category_normalized,
        brand,

        product_url,
        price_mad

    FROM cleaned

),

weekly_stats AS (

    SELECT

        week_start,
        year_num,
        week_num,
        source_platform,
        category_normalized,
        brand,

        COUNT(DISTINCT product_url) AS product_count,
        COUNT(*) AS total_observations,

        ROUND(AVG(price_mad), 2) AS avg_price_mad,
        ROUND(MIN(price_mad), 2) AS min_price_mad,
        ROUND(MAX(price_mad), 2) AS max_price_mad,

        ROUND(STDDEV(price_mad), 2) AS std_price_mad,

        ROUND(APPROX_QUANTILES(price_mad, 100)[OFFSET(50)], 2)
            AS median_price_mad,

        ROUND(APPROX_QUANTILES(price_mad, 100)[OFFSET(25)], 2)
            AS p25_price_mad,

        ROUND(APPROX_QUANTILES(price_mad, 100)[OFFSET(75)], 2)
            AS p75_price_mad

    FROM weekly_base

    GROUP BY
        week_start,
        year_num,
        week_num,
        source_platform,
        category_normalized,
        brand

),

with_weekly_velocity AS (

    SELECT

        *,

        LAG(avg_price_mad) OVER (
            PARTITION BY source_platform, category_normalized
            ORDER BY week_start
        ) AS prev_week_avg,

        ROUND(
            SAFE_DIVIDE(
                avg_price_mad -
                LAG(avg_price_mad) OVER (
                    PARTITION BY source_platform, category_normalized
                    ORDER BY week_start
                ),
                NULLIF(
                    LAG(avg_price_mad) OVER (
                        PARTITION BY source_platform, category_normalized
                        ORDER BY week_start
                    ),
                    0
                )
            ) * 100,
            2
        ) AS weekly_price_velocity_pct,

        ROUND(
            p75_price_mad - p25_price_mad,
            2
        ) AS iqr_price_mad

    FROM weekly_stats

)

SELECT

    TO_HEX(MD5(CONCAT(
        CAST(week_start AS STRING),
        '#',
        source_platform,
        '#',
        category_normalized,
        '#',
        brand
    ))) AS agg_row_key,

    *

FROM with_weekly_velocity