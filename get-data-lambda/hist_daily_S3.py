import boto3
import io
import logging
import pandas as pd
import psycopg2
import requests
from datetime import date, datetime, timedelta
from time import sleep

##########
# 1. Parameters
##########


def read_csv_from_s3(bucket_name, file_name, separator):
    """Read csv from S3 bucket

    Args:
        bucket_name (_type_): name of the bucket
        file_name (_type_): name of the file

    Returns:
        _type_: _description_
    """
    # Initialize AWS S3 client
    s3 = boto3.client('s3')

    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        csv_data = response['Body'].read().decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data), sep=separator)
        return df
    except Exception as e:
        print(f"Error reading CSV from S3: {e}")
        return None


# Get dataframe of S&P tickers - REPLACE BUCKET NAME
df_sp = read_csv_from_s3(
    'bucket_name', 'SP500_sortedList_20230607.csv', '\t')
df_sp.set_index('S.No.', inplace=True)

# Get a list of tickers from S&P500 index sorted descending 
list_sp_tickers = list(df_sp.iloc[:25, 1])

# Get dataframe of connections paramaters - REPLACE BUCKET NAME
df_env = read_csv_from_s3(
    'bucket_name', 'parameter.csv', '|')

# Get API KEY from environment variables
api_key_av = df_env.loc[df_env['parameter']
                        == 'alphavantage', 'value'].values[0]

# Get DB connection parameter
rds_host = df_env.loc[df_env['parameter'] == 'host', 'value'].values[0]
rds_database = df_env.loc[df_env['parameter'] == 'database', 'value'].values[0]
rds_user = df_env.loc[df_env['parameter'] == 'user', 'value'].values[0]
rds_password = df_env.loc[df_env['parameter'] == 'password', 'value'].values[0]

# Logging parameter
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

##########
# 2. Function to get historical daily data per ticker
###########


def get_ticker_daily_history_alphav(symbol: str, api_key, output_size):
    """
    Return trading historical data for specified ticker through Alpha Vantage API call
    and convert data from JSON to DataFrame
    :param symbol: ticker symbol (ex: 'AAPL' for Apple)
    :param api_key: alpha_vantage API key
    :return: DataFrame with historical daily trading data
    """
    # Request API
    base_url = 'https://www.alphavantage.co/query?'
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': output_size,
        'apikey': api_key,
    }

    response = requests.get(base_url, params=params)
    json = response.json()

    # Convert Time Series part into a dataframe
    df_data = pd.DataFrame.from_dict(
        json['Time Series (Daily)'],
        orient='index'
    ).sort_index(axis=1)

    # Include date as dataframe's values by creating a new index
    df_data.reset_index(inplace=True)

    # Change column names
    df_data = df_data.rename(columns={
        'index': 'date_trade',
        '1. open': 'open_value',
        '2. high': 'high_value',
        '3. low': 'low_value',
        '4. close': 'close_value',
        '5. volume': 'volume'
    })

    # Add symbol and date od extraction to dataframe
    df_data['symbol'] = json["Meta Data"]["2. Symbol"]
    df_data['last_refreshed'] = json["Meta Data"]["3. Last Refreshed"]

    # Re-order dataframe
    df_data = df_data[[
        'symbol',
        'last_refreshed',
        'date_trade',
        'open_value',
        'high_value',
        'low_value',
        'close_value',
        'volume'
    ]]

    return df_data


##########
# 3. RDS database functions
##########


def create_db_connection():
    """
    Function to create a connection with RDS database
    :return:
    """
    try:
        conn = psycopg2.connect(
            host=rds_host,
            database=rds_database,
            user=rds_user,
            password=rds_password
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise


def close_db_connection(conn):
    """
    Close connection to database
    :param conn: active connection to database
    :return:
    """
    conn.close()


def copy_dataframe_to_db(conn, data, table_name):
    """
    Load the data in memory in and then in DB in bulk
    :param conn: open connection with DB
    :param data: data to be imported to DB
    :param table_name: DB table name
    :return:
    """
    try:
        # Create a database cursor
        cursor = conn.cursor()

        # Create a temporary CSV file in memory
        csv_buffer = io.StringIO()
        data.to_csv(csv_buffer, index=False, header=False)
        csv_buffer.seek(0)

        # Use the PostgreSQL COPY command to insert data from the CSV
        cursor.copy_expert(f"COPY {table_name} FROM stdin CSV", csv_buffer)

        # Commit the transactions
        conn.commit()

    except Exception as e:
        print(f"Error inserting data into the database: {e}")
        conn.rollback()
        raise


def refresh_view_db(conn, views_names):
    """
    Refreshed materialized view specied as argument
    :param conn: open connection with DB
    :param views_names: List of viewx to be refreshed
    :return:
    """
    try:
        # Create a database cursor
        cursor = conn.cursor()

        for view_name in views_names:
            # Refreshed link materialized view
            cursor.execute(f"REFRESH MATERIALIZED VIEW {view_name};")

        # Commit the transactions
        conn.commit()

    except Exception as e:
        print(f"Error inserting data into the database: {e}")
        conn.rollback()
        raise


def query_db(conn, query):
    """_summary_

    Args:
        conn : connector to database
        query: SQL query to execute within database
    """
    try:
        # Create a database cursor
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute(query)

        # Fetch all the results into a variable
        query_result = cursor.fetchall()

        return query_result

    except Exception as e:
        print(f"Error executing the query: {e}")
        conn.rollback()
        raise


##########
# 4. Lambda function
##########


def historical_daily_data(event, context):
    """Lambda function for AWS

    Args:
        event (_type_): _description_
        context (_type_): _description_

    Returns:
        _type_: _description_
    """

    # Create a database connection
    conn = create_db_connection()

    # Specify the table name where you want to insert the data and view to refresh
    table_name = 'finance.daily_trade'
    views_names = [
        'finance.last_daily_trade',
        'finance.daily_trade_var',
        'finance.daily_trade_1year',
        'finance.light_income_statement',
        'stock_analysis_1year',
    ]

    # Loop on every ticker of the selected S&P 500 list
    for ticker in list_sp_tickers:

        try:

            # Get maximum date from database, dataframe and current date
            query_max_date = f" \
            SELECT MAX(date_trade) \
            FROM finance.daily_trade \
            WHERE symbol = '{ticker}' \
            "
            max_date_db = query_db(conn, query_max_date)[0][0]
            if type(max_date_db) == date:
                max_date_db_str = max_date_db.strftime("%Y-%m-%d")
            else:
                max_date_db_str = '0000-00-00'
            current_date = datetime.now().date()

            # Load data scenario accroding to max date result
            match max_date_db:

                case None:
                    # Generate a DataFrame on 'full' history of data for ticker
                    df_daily_history_alphav = get_ticker_daily_history_alphav(
                        ticker, api_key_av, 'full')
                    # Insert data into the database using the COPY command
                    copy_dataframe_to_db(
                        conn, df_daily_history_alphav, table_name)
                    logger.info(
                        f"Full historical daily data exported successfully for {ticker}")

                case x if x < current_date - timedelta(days=1):
                    # Generate a DataFrame on 100 last records for ticker
                    df_daily_history_alphav = get_ticker_daily_history_alphav(
                        ticker, api_key_av, 'compact')
                    # Filter dataframe and copy to database
                    df_filter = df_daily_history_alphav[df_daily_history_alphav['date_trade']
                                                        > max_date_db_str]
                    copy_dataframe_to_db(conn, df_filter, table_name)
                    logger.info(
                        f"Historical daily data above {max_date_db_str} exported successfully for {ticker}")

                case _:
                    pass
                    logger.info(
                        f"All data already loaded, no action on database for {ticker}")

        # Handle exception and continue
        except Exception as e:
            print(f"An error occurred: {e}")

        # Sleep for 12 seconds as calls to API are limited to 5 per minute
        sleep(12)

    # Refreshed Materialized views
    refresh_view_db(
        conn, views_names)
    logger.info(
        f"Materialized views refreshed")

    # Close the cursor and database connection
    close_db_connection(conn)

    # Create log information
    current_datetime = datetime.now()
    logger.info("Connection with database is closed")
    logger.info(
        f"lambda function for daily data was executed on {current_datetime}")

    return {"statusCode": 200, "message": f"lambda daily_data executed"}
