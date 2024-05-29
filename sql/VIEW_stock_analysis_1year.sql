-- finance.stock_analysis_1year source

CREATE MATERIALIZED VIEW finance.stock_analysis_1year
TABLESPACE pg_default
AS WITH maxdate AS (
         SELECT daily_trade.symbol,
            max(daily_trade.date_trade) AS date_trade
           FROM finance.daily_trade
          GROUP BY daily_trade.symbol
        )
 SELECT dt.symbol,
    max(dt.high_value) AS max_value,
    min(dt.low_value) AS min_value,
    (max(dt.high_value) - min(dt.low_value)) / min(dt.low_value) AS var_highlow_perc,
    max(dt.volume) AS max_volume,
    min(dt.volume) AS min_volume,
    avg(dt.volume) AS average_volume,
    (max(dt.volume) - min(dt.volume))::numeric / min(dt.volume)::numeric AS var_volume_perc,
    avg(dt.close_value) AS average_value,
    stddev_pop(dt.close_value) AS standard_deviation,
    stddev_pop(dt.close_value) / avg(dt.close_value) AS standard_deviation_over_mean
   FROM finance.daily_trade dt
     LEFT JOIN maxdate md ON dt.symbol::text = md.symbol::text
  WHERE dt.date_trade >= (md.date_trade - '1 year'::interval)
  GROUP BY dt.symbol
WITH DATA;