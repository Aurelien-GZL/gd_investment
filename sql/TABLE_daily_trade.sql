-- finance.daily_trade definition

-- Drop table

-- DROP TABLE finance.daily_trade;

CREATE TABLE finance.daily_trade (
	symbol varchar(8) NOT NULL,
	last_refreshed date NOT NULL,
	date_trade date NOT NULL,
	open_value numeric(10, 4) NOT NULL,
	high_value numeric(10, 4) NOT NULL,
	low_value numeric(10, 4) NOT NULL,
	close_value numeric(10, 4) NOT NULL,
	volume int8 NOT NULL,
	CONSTRAINT daily_trade_pkey PRIMARY KEY (symbol, date_trade)
);