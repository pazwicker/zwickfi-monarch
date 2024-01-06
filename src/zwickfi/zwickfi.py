#!.venv/bin/python3.11

import monarch
from bigquery import BigQuery
from monarchmoney import MonarchMoney
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
monarch_email = os.getenv("MONARCH_EMAIL")
monarch_password = os.getenv("MONARCH_PASSWORD")


def login():
    mm = MonarchMoney()
    asyncio.run(mm.login(monarch_email, monarch_password))
    return mm


def zwickfi():
    # log in to monarch
    mm = login()

    # pull various data sets from monarch
    transactions = monarch.transactions.get_transactions(mm)
    transaction_categories = monarch.transaction_categories.get_transaction_categories(
        mm
    )
    transaction_tags = monarch.transaction_tags.get_transaction_tags(mm)

    # write monarch data to bigquery
    tables = [transactions, transaction_categories, transaction_tags]
    table_names = ["transactions", "transaction_categories", "transaction_tags"]

    for i, table in enumerate(tables):
        table_name = table_names[i]
        BigQuery.write_to_bigquery(table, table_name)


zwickfi()
