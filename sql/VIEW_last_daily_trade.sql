-- finance.last_daily_trade source

CREATE MATERIALIZED VIEW finance.last_daily_trade
TABLESPACE pg_default
AS SELECT dt.symbol,
    dt.last_refreshed,
    dt.date_trade,
    dt.open_value,
    dt.high_value,
    dt.low_value,
    dt.close_value,
    dt.volume
   FROM finance.daily_trade dt
  WHERE dt.date_trade = (( SELECT max(dt2.date_trade) AS max
           FROM finance.daily_trade dt2))
WITH DATA;