-- finance.company definition

-- Drop table

-- DROP TABLE finance.company;

CREATE TABLE finance.company (
	symbol varchar(8) NOT NULL,
	company_name varchar(50) NOT NULL,
	sector varchar(100) NOT NULL,
	CONSTRAINT company_pkey PRIMARY KEY (symbol)
);