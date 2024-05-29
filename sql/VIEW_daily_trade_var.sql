-- finance.daily_trade_var source

CREATE MATERIALIZED VIEW finance.daily_trade_var
TABLESPACE pg_default
AS WITH maxdate AS (
         SELECT daily_trade.symbol,
            max(daily_trade.date_trade) AS date_trade
           FROM finance.daily_trade
          GROUP BY daily_trade.symbol
        ), maxdate_1day AS (
         SELECT fdt.symbol,
            max(fdt.date_trade) AS date_trade_prev
           FROM finance.daily_trade fdt
             LEFT JOIN maxdate md_1 ON fdt.symbol::text = md_1.symbol::text
          WHERE fdt.date_trade <= (md_1.date_trade - '1 day'::interval)
          GROUP BY fdt.symbol
        ), maxdate_1month AS (
         SELECT fdt.symbol,
            max(fdt.date_trade) AS date_trade_prev
           FROM finance.daily_trade fdt
             LEFT JOIN maxdate md_1 ON fdt.symbol::text = md_1.symbol::text
          WHERE fdt.date_trade <= (md_1.date_trade - '1 mon'::interval)
          GROUP BY fdt.symbol
        ), maxdate_3months AS (
         SELECT fdt.symbol,
            max(fdt.date_trade) AS date_trade_prev
           FROM finance.daily_trade fdt
             LEFT JOIN maxdate md_1 ON fdt.symbol::text = md_1.symbol::text
          WHERE fdt.date_trade <= (md_1.date_trade - '3 mons'::interval)
          GROUP BY fdt.symbol
        ), maxdate_6months AS (
         SELECT fdt.symbol,
            max(fdt.date_trade) AS date_trade_prev
           FROM finance.daily_trade fdt
             LEFT JOIN maxdate md_1 ON fdt.symbol::text = md_1.symbol::text
          WHERE fdt.date_trade <= (md_1.date_trade - '6 mons'::interval)
          GROUP BY fdt.symbol
        ), maxdate_1year AS (
         SELECT fdt.symbol,
            max(fdt.date_trade) AS date_trade_prev
           FROM finance.daily_trade fdt
             LEFT JOIN maxdate md_1 ON fdt.symbol::text = md_1.symbol::text
          WHERE fdt.date_trade <= (md_1.date_trade - '1 year'::interval)
          GROUP BY fdt.symbol
        ), maxdate_5years AS (
         SELECT fdt.symbol,
            max(fdt.date_trade) AS date_trade_prev
           FROM finance.daily_trade fdt
             LEFT JOIN maxdate md_1 ON fdt.symbol::text = md_1.symbol::text
          WHERE fdt.date_trade <= (md_1.date_trade - '5 years'::interval)
          GROUP BY fdt.symbol
        ), maxdate_10years AS (
         SELECT fdt.symbol,
            max(fdt.date_trade) AS date_trade_prev
           FROM finance.daily_trade fdt
             LEFT JOIN maxdate md_1 ON fdt.symbol::text = md_1.symbol::text
          WHERE fdt.date_trade <= (md_1.date_trade - '10 years'::interval)
          GROUP BY fdt.symbol
        ), maxdate_20years AS (
         SELECT fdt.symbol,
            max(fdt.date_trade) AS date_trade_prev
           FROM finance.daily_trade fdt
             LEFT JOIN maxdate md_1 ON fdt.symbol::text = md_1.symbol::text
          WHERE fdt.date_trade <= (md_1.date_trade - '20 years'::interval)
          GROUP BY fdt.symbol
        )
 SELECT md.symbol,
    md.date_trade,
    dt.close_value,
    md1d.date_trade_prev AS date_trade_1day,
    dt1d.close_value AS close_value_1day,
    dt.close_value - dt1d.close_value AS var_1day,
    round((dt.close_value - dt1d.close_value) / dt1d.close_value * 100::numeric, 2) AS var_1day_perc,
    md1m.date_trade_prev AS date_trade_1month,
    dt1m.close_value AS close_value_1month,
    dt.close_value - dt1m.close_value AS var_1month,
    round((dt.close_value - dt1m.close_value) / dt1m.close_value * 100::numeric, 2) AS var_1month_perc,
    md3m.date_trade_prev AS date_trade_3months,
    dt3m.close_value AS close_value_3months,
    dt.close_value - dt3m.close_value AS var_3months,
    round((dt.close_value - dt3m.close_value) / dt3m.close_value * 100::numeric, 2) AS var_3months_perc,
    md6m.date_trade_prev AS date_trade_6months,
    dt6m.close_value AS close_value_6months,
    dt.close_value - dt6m.close_value AS var_6months,
    round((dt.close_value - dt6m.close_value) / dt6m.close_value * 100::numeric, 2) AS var_6months_perc,
    md1y.date_trade_prev AS date_trade_1year,
    dt1y.close_value AS close_value_1year,
    dt.close_value - dt1y.close_value AS var_1year,
    round((dt.close_value - dt1y.close_value) / dt1y.close_value * 100::numeric, 2) AS var_1year_perc,
    md5y.date_trade_prev AS date_trade_5years,
    dt5y.close_value AS close_value_5years,
    dt.close_value - dt5y.close_value AS var_5years,
    round((dt.close_value - dt5y.close_value) / dt5y.close_value * 100::numeric, 2) AS var_5years_perc,
    md10y.date_trade_prev AS date_trade_10years,
    dt10y.close_value AS close_value_10years,
    dt.close_value - dt10y.close_value AS var_10years,
    round((dt.close_value - dt10y.close_value) / dt10y.close_value * 100::numeric, 2) AS var_10years_perc,
    md20y.date_trade_prev AS date_trade_20years,
    dt20y.close_value AS close_value_20years,
    dt.close_value - dt20y.close_value AS var_20years,
    round((dt.close_value - dt20y.close_value) / dt20y.close_value * 100::numeric, 2) AS var_20years_perc
   FROM maxdate md
     LEFT JOIN maxdate_1day md1d ON md.symbol::text = md1d.symbol::text
     LEFT JOIN maxdate_1month md1m ON md.symbol::text = md1m.symbol::text
     LEFT JOIN maxdate_3months md3m ON md.symbol::text = md3m.symbol::text
     LEFT JOIN maxdate_6months md6m ON md.symbol::text = md6m.symbol::text
     LEFT JOIN maxdate_1year md1y ON md.symbol::text = md1y.symbol::text
     LEFT JOIN maxdate_5years md5y ON md.symbol::text = md5y.symbol::text
     LEFT JOIN maxdate_10years md10y ON md.symbol::text = md10y.symbol::text
     LEFT JOIN maxdate_20years md20y ON md.symbol::text = md20y.symbol::text
     LEFT JOIN finance.daily_trade dt ON md.symbol::text = dt.symbol::text AND md.date_trade = dt.date_trade
     LEFT JOIN finance.daily_trade dt1d ON md.symbol::text = dt1d.symbol::text AND md1d.date_trade_prev = dt1d.date_trade
     LEFT JOIN finance.daily_trade dt1m ON md.symbol::text = dt1m.symbol::text AND md1m.date_trade_prev = dt1m.date_trade
     LEFT JOIN finance.daily_trade dt3m ON md.symbol::text = dt3m.symbol::text AND md3m.date_trade_prev = dt3m.date_trade
     LEFT JOIN finance.daily_trade dt6m ON md.symbol::text = dt6m.symbol::text AND md6m.date_trade_prev = dt6m.date_trade
     LEFT JOIN finance.daily_trade dt1y ON md.symbol::text = dt1y.symbol::text AND md1y.date_trade_prev = dt1y.date_trade
     LEFT JOIN finance.daily_trade dt5y ON md.symbol::text = dt5y.symbol::text AND md5y.date_trade_prev = dt5y.date_trade
     LEFT JOIN finance.daily_trade dt10y ON md.symbol::text = dt10y.symbol::text AND md10y.date_trade_prev = dt10y.date_trade
     LEFT JOIN finance.daily_trade dt20y ON md.symbol::text = dt20y.symbol::text AND md20y.date_trade_prev = dt20y.date_trade
  ORDER BY (round((dt.close_value - dt1d.close_value) / dt1d.close_value * 100::numeric, 2)) DESC
WITH DATA;