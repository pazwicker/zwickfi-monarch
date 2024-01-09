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
    mm = MonarchMoney(timeout=30)
    asyncio.run(mm.login(monarch_email, monarch_password))
    return mm


def zwickfi():
    # log in to monarch
    mm = login()

    # pull transactional data sets from monarch
    total_transactions = monarch.Transactions.get_total_transactions(mm)
    transactions = monarch.Transactions.get_transactions(mm, limit=total_transactions)
    transaction_categories = monarch.Transactions.get_transaction_categories(
        mm
    )
    transaction_tags = monarch.Transactions.get_transaction_tags(mm)

    # write monarch data to bigquery
    tables = [transactions, transaction_categories, transaction_tags]
    table_names = ["transactions", "transaction_categories", "transaction_tags"]

    for i, table in enumerate(tables):
        table_name = table_names[i]
        BigQuery.write_to_bigquery(table, table_name)


zwickfi()
