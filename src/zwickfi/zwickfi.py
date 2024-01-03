#!.venv/bin/python3.11

from transactions import zwickfi_transactions
from bigquery import BigQuery
from monarchmoney import MonarchMoney
from dotenv import load_dotenv
import asyncio
import os
import json

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
    tables = [transactions]
    table_names = ['transactions']

    for i, table in enumerate(tables):
        table_name = table_names[i]
        BigQuery.write_to_bigquery(table, table_name)


zwickfi()
