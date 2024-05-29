from django.db import models


# Manager to define composite key for daily Trade
class DailyTradeManager(models.Manager):
    def get_by_natural_key(self, symbol, date_trade):
        return self.get(symbol=symbol, date_trade=date_trade)


##########
# Parent models
##########

# Parent model for daily trades
class TradeBase(models.Model):

    # Define all fields and datatypes corresponding to the one already in place in DB
    # Declare first field of composite key as primary key
    symbol = models.CharField(primary_key=True, max_length=8)
    last_refreshed = models.DateField()
    date_trade = models.DateField()
    open_value = models.DecimalField(max_digits=10, decimal_places=4)
    high_value = models.DecimalField(max_digits=10, decimal_places=4)
    low_value = models.DecimalField(max_digits=10, decimal_places=4)
    close_value = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.BigIntegerField()

    class Meta:
        abstract = True
        

# Parent model for company
class CompanyBase(models.Model):

    # Define all fields and datatypes corresponding to the one already in place in DB
    symbol = models.CharField(primary_key=True, max_length=8)
    company_name = models.CharField(max_length=50)
    sector = models.CharField(max_length=100)

    class Meta:
        abstract = True

        
# Parent model for income statement
class IncomeStatementBase(models.Model):

    # Define all fields and datatypes corresponding to the one already in place in DB
    symbol = models.CharField(primary_key=True, max_length=8)
    fiscal_date_ending = models.DateField()
    total_revenue = models.BigIntegerField()
    cost_of_goods_and_services_sold = models.BigIntegerField()
    operating_income = models.BigIntegerField()
    depreciation_and_amortization = models.BigIntegerField()
    income_tax_expense = models.BigIntegerField()
    interest_and_debt_expense = models.BigIntegerField()
    netincome = models.BigIntegerField()
    ebit = models.BigIntegerField()
    ebitda = models.BigIntegerField()

    class Meta:
        abstract = True


# Parent model for stock analysis
class StockAnalysisBase(models.Model):

    # Define all fields and datatypes corresponding to the one already in place in DB
    symbol = models.CharField(primary_key=True, max_length=8)
    max_value = models.DecimalField(max_digits=10, decimal_places=4)
    min_value = models.DecimalField(max_digits=10, decimal_places=4)
    var_highlow_perc = models.DecimalField(max_digits=10, decimal_places=4)
    max_volume = models.BigIntegerField()
    min_volume = models.BigIntegerField()
    average_volume = models.DecimalField(max_digits=10, decimal_places=4)
    var_volume_perc = models.DecimalField(max_digits=10, decimal_places=4)
    average_value = models.DecimalField(max_digits=10, decimal_places=4)
    standard_deviation = models.DecimalField(max_digits=10, decimal_places=4)
    standard_deviation_over_mean = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        abstract = True


# Parent model for daily trades variances
class TradeVar(models.Model):

    # Define all fields and datatypes corresponding to the one already in place in DB
    symbol = models.CharField(primary_key=True, max_length=8)
    date_trade = models.DateField()
    close_value = models.DecimalField(max_digits=10, decimal_places=4)
    # 1 day
    date_trade_1day = models.DateField()
    close_value_1day = models.DecimalField(max_digits=10, decimal_places=4)
    var_1day = models.DecimalField(max_digits=10, decimal_places=4)
    var_1day_perc = models.DecimalField(max_digits=10, decimal_places=4)
    # 1 month
    date_trade_1month = models.DateField()
    close_value_1month = models.DecimalField(max_digits=10, decimal_places=4)
    var_1month = models.DecimalField(max_digits=10, decimal_places=4)
    var_1month_perc = models.DecimalField(max_digits=10, decimal_places=4)
    # 3 months
    date_trade_3months = models.DateField()
    close_value_3months = models.DecimalField(max_digits=10, decimal_places=4)
    var_3months = models.DecimalField(max_digits=10, decimal_places=4)
    var_3months_perc = models.DecimalField(max_digits=10, decimal_places=4)
    # 6 months
    date_trade_6months = models.DateField()
    close_value_6months = models.DecimalField(max_digits=10, decimal_places=4)
    var_6months = models.DecimalField(max_digits=10, decimal_places=4)
    var_6months_perc = models.DecimalField(max_digits=10, decimal_places=4)
    # 1 year
    date_trade_1year = models.DateField()
    close_value_1year = models.DecimalField(max_digits=10, decimal_places=4)
    var_1year = models.DecimalField(max_digits=10, decimal_places=4)
    var_1year_perc = models.DecimalField(max_digits=10, decimal_places=4)
    # 5 years
    date_trade_5years = models.DateField()
    close_value_5years = models.DecimalField(max_digits=10, decimal_places=4)
    var_5years = models.DecimalField(max_digits=10, decimal_places=4)
    var_5years_perc = models.DecimalField(max_digits=10, decimal_places=4)
    # 10 years
    date_trade_10years = models.DateField()
    close_value_10years = models.DecimalField(max_digits=10, decimal_places=4)
    var_10years = models.DecimalField(max_digits=10, decimal_places=4)
    var_10years_perc = models.DecimalField(max_digits=10, decimal_places=4)
    # 20 years
    date_trade_20years = models.DateField()
    close_value_20years = models.DecimalField(max_digits=10, decimal_places=4)
    var_20years = models.DecimalField(max_digits=10, decimal_places=4)
    var_20years_perc = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        managed = False  # Indicate Django not to manage this table
        db_table = 'daily_trade_var'


##########
# Child and models for tables and views
##########

# Model for daily trade table inheriting TradeBase class
# ----------
class DailyTrade(TradeBase):

    # Add a custom manager to the model
    objects = DailyTradeManager()

    # Model properties
    class Meta:
        managed = False     # Indicate Django not to manage this table
        db_table = 'daily_trade'    # Define table name in database
        unique_together = ('symbol', 'date_trade')  # Provide composite key
        auto_created = True     # Cancel auto-creation of an 'id' field

    # Define output representing the objet
    def __str__(self):
        return f'{self.symbol} - {self.date_trade}'


# Model for last daily trade view
# ----------
class DailyTradeLast(TradeBase):

    class Meta:
        managed = False  # Indicate Django not to manage this table
        db_table = 'last_daily_trade'


# Model for daily trade 1 year view
# ----------
class DailyTrade1Year(TradeBase):
    
    # Add a custom manager to the model
    objects = DailyTradeManager()

    class Meta:
        managed = False  # Indicate Django not to manage this table
        db_table = 'daily_trade_1year'
        unique_together = ('symbol', 'date_trade')  # Provide composite key
        

# Model for company year view
# ----------
class Company(CompanyBase):

    class Meta:
        managed = False  # Indicate Django not to manage this table
        db_table = 'company'
        auto_created = True     # Cancel auto-creation of an 'id' field
        

# Model for light_income_statement view
# ----------
class IncomeStatement(IncomeStatementBase):

    class Meta:
        managed = False  # Indicate Django not to manage this table
        db_table = 'light_income_statement'
        

# Model for stock_analysis_1year view
# ----------
class StockAnalysis1Year(StockAnalysisBase):

    class Meta:
        managed = False  # Indicate Django not to manage this table
        db_table = 'stock_analysis_1year'
        

