#!.venv/bin/python3.11

from monarch import monarch
from bigquery import BigQuery
from monarchmoney import MonarchMoney
from dotenv import load_dotenv
import asyncio
import os
from google.cloud import secretmanager

load_dotenv()
monarch_email = os.getenv("MONARCH_EMAIL")
monarch_password = os.getenv("MONARCH_PASSWORD")

def access_secret_version(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(name=secret_name)
    return response.payload.data.decode('UTF-8')

def login():
    mm = MonarchMoney(timeout=30)
    try:
        asyncio.run(mm.login(monarch_email, monarch_password))
    except:
        gcp_monarch_email = access_secret_version('MONARCH_EMAIL')
        gcp_monarch_password = access_secret_version('MONARCH_PASSWORD')
        asyncio.run(mm.login(gcp_monarch_email, gcp_monarch_password))
    return mm


def zwickfi():
    # log in to monarch
    mm = login()

    # pull transactional data sets from monarch
    total_transactions = monarch.Transactions.get_total_transactions(mm)
    transactions = monarch.Transactions.get_transactions(mm, limit=total_transactions)
    transaction_categories = monarch.Transactions.get_transaction_categories(mm)
    transaction_tags = monarch.Transactions.get_transaction_tags(mm)

    # write monarch data to bigquery
    tables = [transactions, transaction_categories, transaction_tags]
    table_names = ["transactions", "transaction_categories", "transaction_tags"]

    for i, table in enumerate(tables):
        table_name = table_names[i]
        BigQuery.write_to_bigquery(table, table_name)


zwickfi()
