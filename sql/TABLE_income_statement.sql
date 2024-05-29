-- finance.income_statement definition

-- Drop table

-- DROP TABLE finance.income_statement;

CREATE TABLE finance.income_statement (
	symbol varchar(8) NOT NULL,
	fiscal_date_ending date NOT NULL,
	reported_currency varchar(3) NULL,
	gross_profit int8 NULL,
	total_revenue int8 NULL,
	cost_of_revenue int8 NULL,
	cost_of_goods_and_services_sold int8 NULL,
	operating_income int8 NULL,
	selling_general_and_administrative int8 NULL,
	research_and_development int8 NULL,
	operating_expenses int8 NULL,
	investment_income_net int8 NULL,
	net_interest_income int8 NULL,
	interest_income int8 NULL,
	interest_expense int8 NULL,
	non_interest_income int8 NULL,
	other_non_operating_income int8 NULL,
	depreciation int8 NULL,
	depreciation_and_amortization int8 NULL,
	income_before_tax int8 NULL,
	income_tax_expense int8 NULL,
	interest_and_debt_expense int8 NULL,
	net_income_from_continuing_operations int8 NULL,
	comprehensive_income_net_of_tax int8 NULL,
	ebit int8 NULL,
	ebitda int8 NULL,
	netincome int8 NULL,
	CONSTRAINT income_statement_pkey PRIMARY KEY (symbol, fiscal_date_ending)
);