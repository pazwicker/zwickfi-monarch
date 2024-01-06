#!.venv/bin/python3.11

from transactions import zwickfi_transactions
from bigquery import BigQuery
from categories import zwickfi_transaction_categories
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
    mm = login()
    transactions = zwickfi_transactions.get_transactions(mm)
    transaction_categories = zwickfi_transaction_categories.get_transaction_categories(
        mm
    )
    tables = [transactions, transaction_categories]
    table_names = ["transactions", "transaction_categories"]

    for i, table in enumerate(tables):
        table_name = table_names[i]
        BigQuery.write_to_bigquery(table, table_name)


zwickfi()
