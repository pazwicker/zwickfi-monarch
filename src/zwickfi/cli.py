"""Main CLI entry point for zwickfi-monarch data sync."""

from datetime import date

import pandas as pd

from . import bigquery, forecasts, monarch
from .auth import get_bigquery_client, get_monarch_client


def main() -> None:
    """
    Run the full data sync pipeline.

    1. Authenticate with Google Cloud and Monarch Money
    2. Extract data from Monarch Money API
    3. Generate credit card spending forecasts
    4. Load all data to BigQuery
    """
    # Authenticate
    try:
        bq_client = get_bigquery_client()
    except Exception as e:
        print(f"Failed to authenticate with Google Cloud: {e}")
        return

    mm = get_monarch_client()
    print("Logged into Monarch.")

    # Extract transaction data
    total_transactions = monarch.get_total_transactions(mm)
    transactions = monarch.get_transactions(mm, limit=total_transactions)
    transaction_categories = monarch.get_transaction_categories(mm)
    transaction_tags = monarch.get_transaction_tags(mm)

    # Extract account data
    accounts = monarch.get_accounts(mm)

    # Extract budget data
    budgets = monarch.get_budgets(mm)

    # Extract account history for all accounts
    account_ids = accounts["id"].tolist()
    account_history = pd.DataFrame()

    for account_id in account_ids:
        print(f"Getting account history for account ID {account_id}.")
        history = monarch.get_account_history(mm, account_id)
        account_history = pd.concat([account_history, history], ignore_index=True)

    # Generate forecasts
    forecast_data, credit_cards = forecasts.get_forecast_data(bq_client)
    forecast_df = forecasts.generate_forecasts(forecast_data, credit_cards)

    # Load to BigQuery
    today = date.today()
    datasets = [
        (transactions, "monarch_money", "transactions"),
        (transaction_categories, "monarch_money", "transaction_categories"),
        (transaction_tags, "monarch_money", "transaction_tags"),
        (accounts, "monarch_money", "accounts"),
        (budgets, "monarch_money", "budgets"),
        (account_history, "monarch_money", "account_balance_history"),
        (forecast_df, "forecasts", f"credit_card_forecast_{today}"),
    ]

    for df, schema, table_name in datasets:
        bigquery.write_to_bigquery(df, schema, table_name, bq_client)


if __name__ == "__main__":
    main()
