-- finance.light_income_statement source

CREATE MATERIALIZED VIEW finance.light_income_statement
TABLESPACE pg_default
AS SELECT DISTINCT ON (is2.symbol) is2.symbol,
    is2.fiscal_date_ending,
    is2.total_revenue,
    is2.cost_of_goods_and_services_sold,
    is2.operating_income,
    is2.depreciation_and_amortization,
    is2.income_tax_expense,
    is2.interest_and_debt_expense,
    is2.netincome,
    is2.ebit,
    is2.ebitda
   FROM finance.income_statement is2
  ORDER BY is2.symbol, is2.fiscal_date_ending DESC
WITH DATA;