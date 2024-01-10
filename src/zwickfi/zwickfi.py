#!.venv/bin/python3.11

from monarch import monarch
from bigquery import BigQuery
from monarchmoney import MonarchMoney
import asyncio
from google.cloud import secretmanager

gcp_project_id = 333216132519


def access_secret_version(project_id, secret_name, version_number):
    """
    Access a specific version of a secret stored in Google Cloud Secret Manager.

    Args:
        project_id (int): Google Cloud project ID.
        secret_name (str): Name of the secret to access.
        version_number (int or str): Version number of the secret.

    Returns:
        str: The secret's value as a string.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_name, version_number)
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")


def monarch_login():
    """
    Logs in to the Monarch Money service using credentials stored in Secret Manager.

    Returns:
        MonarchMoney: An authenticated MonarchMoney object.
    """
    mm = MonarchMoney(timeout=30)
    gcp_monarch_email = access_secret_version(gcp_project_id, "MONARCH_EMAIL", 1)
    gcp_monarch_password = access_secret_version(gcp_project_id, "MONARCH_PASSWORD", 1)
    asyncio.run(mm.login(gcp_monarch_email, gcp_monarch_password))
    return mm


def zwickfi():
    """
    Main function to handle the process of logging in to Monarch, retrieving transactions,
    categories, and tags, and then writing this data to BigQuery tables.
    """
    # Log in to monarch
    mm = monarch_login()

    # Pull transactional data sets from monarch
    total_transactions = monarch.Transactions.get_total_transactions(mm)
    transactions = monarch.Transactions.get_transactions(mm, limit=total_transactions)
    transaction_categories = monarch.Transactions.get_transaction_categories(mm)
    transaction_tags = monarch.Transactions.get_transaction_tags(mm)

    # Write monarch data to bigquery
    tables = [transactions, transaction_categories, transaction_tags]
    table_names = ["transactions", "transaction_categories", "transaction_tags"]

    for i, table in enumerate(tables):
        table_name = table_names[i]
        BigQuery.write_to_bigquery(table, table_name)


zwickfi()
