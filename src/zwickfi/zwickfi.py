#!.venv/bin/python3.11

from monarch import monarch
from bigquery import BigQuery
from monarchmoney import MonarchMoney
import asyncio
import os
import pandas as pd
from forecasts import Forecasts
from dotenv import load_dotenv
from datetime import date
from google.oauth2 import service_account
from google.cloud import bigquery

# Load environment variables
load_dotenv()

# Set up global variables
today = date.today()

def get_project_root():
    """
    Returns the root directory of the project.
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_secrets_from_file(secrets_file_path):
    """
    Load secrets from a local file in the /secrets folder.

    Args:
        secrets_file_path (str): Path to the secrets file.

    Returns:
        dict: A dictionary containing the secrets.
    """
    secrets = {}
    try:
        with open(secrets_file_path, 'r') as file:
            for line in file:
                # Split the line into key and value
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    secrets[key] = value
    except FileNotFoundError:
        print(f"Secrets file not found: {secrets_file_path}")
    return secrets


def monarch_login():
    """
    Logs in to the Monarch Money service using credentials stored in a secrets file.

    Returns:
        MonarchMoney: An authenticated MonarchMoney object.
    """
    mm = MonarchMoney(timeout=60)
    
    # Determine the root directory of the project
    project_root = get_project_root()
    
    # Path to the local secrets file relative to the project root
    secrets_file_path = os.path.join(project_root, "secrets", "monarch_secrets.env")
    
    # Load secrets from the local file
    secrets = load_secrets_from_file(secrets_file_path)
    monarch_email = secrets.get("MONARCH_EMAIL")
    monarch_password = secrets.get("MONARCH_PASSWORD")
    
    if not monarch_email or not monarch_password:
        raise ValueError("MONARCH_EMAIL or MONARCH_PASSWORD not found in secrets file.")
    
    try:
        asyncio.run(mm.login(monarch_email, monarch_password))
        print("Logged in to Monarch Money using local secrets file.")
    except Exception as e:
        print(f"Failed to log in to Monarch Money: {e}")
    return mm


def authenticate_with_google_cloud():
    """
    Authenticates with Google Cloud using a service account file.

    Returns:
        bigquery.Client: An authenticated BigQuery client.
    """
    # Determine the root directory of the project
    project_root = get_project_root()
    
    # Path to the service account file relative to the project root
    service_account_file = os.path.join(project_root, "secrets", "service_account.json")
    
    # Check if the service account file exists
    if not os.path.exists(service_account_file):
        raise FileNotFoundError(f"Service account file not found: {service_account_file}")
    
    # Authenticate using the service account file
    credentials = service_account.Credentials.from_service_account_file(service_account_file)
    
    # Create a BigQuery client
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    
    print("Authenticated with Google Cloud using service account file.")
    return client

def zwickfi():
    """
    Main function to handle the process of logging in to Monarch, retrieving transactions,
    categories, and tags, and then writing this data to BigQuery tables.
    """
    try:
        # Authenticate with Google Cloud
        bq_client = authenticate_with_google_cloud()
        print('Authenticated with Google Cloud.')
    except Exception as e:
        print(f"Failed to authenticate with Google Cloud: {e}")
        return

    # Log in to Monarch
    mm = monarch_login()
    print('Logged into Monarch.')

    # Pull transactional data sets from Monarch
    total_transactions = monarch.Transactions.get_total_transactions(mm)
    transactions = monarch.Transactions.get_transactions(mm, limit=total_transactions)
    transaction_categories = monarch.Transactions.get_transaction_categories(mm)
    transaction_tags = monarch.Transactions.get_transaction_tags(mm)

    # Pull account data sets from Monarch
    accounts = monarch.Accounts.get_accounts(mm)

    # Pull account history for each account
    account_ids = accounts['id'].tolist()

    account_history = pd.DataFrame()

    for account_id in account_ids:
        print(f"Getting account history for account ID {account_id}.")
        account_history_temp = monarch.Accounts.get_account_history(mm, account_id)
        account_history = pd.concat([account_history, account_history_temp])

    # Forecast credit card spending using the updated Forecasts class
    forecasts_instance = Forecasts(bq_client)
    forecast_data, credit_cards = forecasts_instance.get_forecast_data()
    forecasts = forecasts_instance.get_forecasts(forecast_data, credit_cards)

    # Write Monarch data to BigQuery
    # Write monarch data to bigquery
    tables = [
        transactions,
        transaction_categories,
        transaction_tags,
        accounts,
        account_history,
        forecasts
    ]
    table_names = [
        "transactions",
        "transaction_categories",
        "transaction_tags",
        "accounts",
        "account_balance_history",
        f"credit_card_forecast_{today}"
    ]
    schema_names = [
        "monarch_money",
        "monarch_money",
        "monarch_money",
        "monarch_money",
        "monarch_money",
        "forecasts"
    ]

    for i, table in enumerate(tables):
        table_name = table_names[i]
        schema_name = schema_names[i]
        BigQuery.write_to_bigquery(table, schema_name, table_name, bq_client)


zwickfi()
