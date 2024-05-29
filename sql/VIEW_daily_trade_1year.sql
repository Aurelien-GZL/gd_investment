-- finance.daily_trade_1year source

CREATE MATERIALIZED VIEW finance.daily_trade_1year
TABLESPACE pg_default
AS WITH maxdate AS (
         SELECT daily_trade.symbol,
            max(daily_trade.date_trade) AS date_trade
           FROM finance.daily_trade
          GROUP BY daily_trade.symbol
        )
 SELECT dt.symbol,
    dt.last_refreshed,
    dt.date_trade,
    dt.open_value,
    dt.high_value,
    dt.low_value,
    dt.close_value,
    dt.volume
   FROM finance.daily_trade dt
     LEFT JOIN maxdate md ON dt.symbol::text = md.symbol::text
  WHERE dt.date_trade >= (md.date_trade - '1 year'::interval)
WITH DATA;