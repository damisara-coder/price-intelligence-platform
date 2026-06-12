-- =============================================================
-- ANALYSE dbt: price_intelligence_insights.sql
-- Description: Requêtes analytiques avancées à destination du
--              dashboard et des notebooks. Non matérialisées.
-- Usage: dbt compile --select analyses/price_intelligence_insights
-- =============================================================

-- ── 1. Top 10 produits avec la plus grande variation de prix ──
WITH top_volatile AS (
    SELECT
        product_name,
        source_platform,
        category_normalized,
        MAX(avg_price_mad) - MIN(avg_price_mad) AS price_range_mad,
        ROUND((MAX(avg_price_mad) - MIN(avg_price_mad)) / NULLIF(MIN(avg_price_mad), 0) * 100, 1) AS price_range_pct,
        COUNT(DISTINCT price_date) AS days_observed
    FROM {{ ref('agg_daily_prices') }}
    GROUP BY product_name, source_platform, category_normalized
    HAVING days_observed >= 3
    ORDER BY price_range_pct DESC
    LIMIT 10
),

platform_comparison AS (
    SELECT
        category_normalized,
        source_platform,
        ROUND(AVG(avg_price_mad), 2) AS avg_price,
        COUNT(DISTINCT product_url) AS product_count
    FROM {{ ref('agg_daily_prices') }}
    WHERE price_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    GROUP BY category_normalized, source_platform
),

recent_alerts AS (
    SELECT
        product_name,
        source_platform,
        category_normalized,
        price_date,
        close_price_mad,
        prev_day_price,
        price_change_pct
    FROM {{ ref('agg_daily_prices') }}
    WHERE is_price_alert = TRUE
      AND price_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    ORDER BY ABS(price_change_pct) DESC
    LIMIT 20
),

weekly_trend AS (
    SELECT
        week_start,
        category_normalized,
        source_platform,
        avg_price_mad,
        weekly_price_velocity_pct,
        product_count
    FROM {{ ref('agg_weekly_category_stats') }}
    WHERE week_start >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
    ORDER BY week_start DESC, category_normalized
)

SELECT
    'ALERTS' AS analysis_type,
    product_name,
    source_platform,
    category_normalized,
    CAST(price_date AS STRING) AS date_str,
    close_price_mad AS current_price,
    prev_day_price,
    price_change_pct
FROM recent_alerts

UNION ALL

SELECT
    'VOLATILE' AS analysis_type,
    product_name,
    source_platform,
    category_normalized,
    CAST(days_observed AS STRING) AS date_str,
    price_range_mad AS current_price,
    NULL AS prev_day_price,
    price_range_pct AS price_change_pct
FROM top_volatile