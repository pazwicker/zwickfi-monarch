#!.venv/bin/python3.11

from monarch import monarch
from bigquery import BigQuery
from monarchmoney import MonarchMoney, RequireMFAException
import asyncio
import os
import pandas as pd
from forecasts import Forecasts
from datetime import date
from google.oauth2 import service_account
from google.cloud import bigquery

# Set up global variables
today = date.today()


def monarch_login():
    """
    Logs in to the Monarch Money service using credentials from environment variables.
    If the environment variables are not set, prompts the user to enter them.

    Returns:
        MonarchMoney: An authenticated MonarchMoney object.
    """
    mm = MonarchMoney(timeout=60)

    # Attempt to retrieve credentials from environment variables
    monarch_email = os.getenv("MONARCH_EMAIL")
    monarch_password = os.getenv("MONARCH_PASSWORD")
    monarch_secret_key = os.getenv("MONARCH_SECRET_KEY")

    # Prompt the user if environment variables are not set
    if not monarch_email:
        monarch_email = input(
            "The environment variable 'MONARCH_EMAIL' is not set.\n"
            "Please enter your Monarch Money email: "
        ).strip()
        while not monarch_email:
            monarch_email = input(
                "Email cannot be empty. Please enter your Monarch Money email: "
            ).strip()

    if not monarch_password:
        monarch_password = input(
            "The environment variable 'MONARCH_PASSWORD' is not set.\n"
            "Please enter your Monarch Money password: "
        ).strip()
        while not monarch_password:
            monarch_password = input(
                "Password cannot be empty. Please enter your Monarch Money password: "
            ).strip()

    if not monarch_secret_key:
        monarch_secret_key = input(
            "The environment variable 'MONARCH_SECRET_KEY' is not set.\n"
            "Please enter your Monarch Money secret key: "
        ).strip()
        while not monarch_secret_key:
            monarch_secret_key = input(
                "Secret key cannot be empty. Please enter your Monarch Money secret key: "
            ).strip()

    # Attempt to log in with the provided credentials
    try:
        asyncio.run(
            mm.login(
                email=monarch_email,
                password=monarch_password,
                save_session=False,
                use_saved_session=False,
                mfa_secret_key=monarch_secret_key,
            )
        )
        print("Successfully logged in to Monarch Money.")
    except Exception as e:
        print(f"Failed to log in to Monarch Money: {e}")
        raise

    return mm


def authenticate_with_google_cloud():
    """
    Authenticates with Google Cloud using a service account file specified by
    the GOOGLE_APPLICATION_CREDENTIALS environment variable. Prompts the user
    to provide the path if the variable is not set.

    Returns:
        bigquery.Client: An authenticated BigQuery client.
    """
    # Check if the environment variable is set
    service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not service_account_file:
        # Prompt the user for the path if the variable is not set
        service_account_file = input(
            "The environment variable 'GOOGLE_APPLICATION_CREDENTIALS' is not set.\n"
            "Please provide the full path to your service_account.json file: "
        )
        # Validate the user-provided path
        if not os.path.exists(service_account_file):
            raise FileNotFoundError(
                f"Service account file not found: {service_account_file}"
            )

        # Optionally, set the environment variable for future use in this session
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_file

    # Authenticate using the service account file
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file
    )
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
        print("Authenticated with Google Cloud.")
    except Exception as e:
        print(f"Failed to authenticate with Google Cloud: {e}")
        return

    # Log in to Monarch
    mm = monarch_login()
    print("Logged into Monarch.")

    # Pull transactional data sets from Monarch
    total_transactions = monarch.Transactions.get_total_transactions(mm)
    transactions = monarch.Transactions.get_transactions(mm, limit=total_transactions)
    transaction_categories = monarch.Transactions.get_transaction_categories(mm)
    transaction_tags = monarch.Transactions.get_transaction_tags(mm)

    # Pull account data sets from Monarch
    accounts = monarch.Accounts.get_accounts(mm)

    # Pull budget data from Monarch
    budgets = monarch.Budgets.get_budgets(mm)

    # Pull account history for each account
    account_ids = accounts["id"].tolist()

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
    tables = [
        transactions,
        transaction_categories,
        transaction_tags,
        accounts,
        budgets,
        account_history,
        forecasts,
    ]
    table_names = [
        "transactions",
        "transaction_categories",
        "transaction_tags",
        "accounts",
        "budgets",
        "account_balance_history",
        f"credit_card_forecast_{today}",
    ]
    schema_names = [
        "monarch_money",
        "monarch_money",
        "monarch_money",
        "monarch_money",
        "monarch_money",
        "monarch_money",
        "forecasts",
    ]

    for i, table in enumerate(tables):
        table_name = table_names[i]
        schema_name = schema_names[i]
        BigQuery.write_to_bigquery(table, schema_name, table_name, bq_client)


zwickfi()
