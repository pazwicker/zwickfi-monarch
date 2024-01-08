import pandas as pd
import asyncio
from typing import Optional
import math


class TransactionCategories(object):
    def get_transaction_categories(mm):
        categories = asyncio.run(mm.get_transaction_categories())
        df = pd.json_normalize(categories["categories"])
        df.columns = df.columns.str.replace(".", "_")
        return df


class Transactions(object):
    def get_transactions(mm, limit: Optional[int] = 1000):
        max_results = 1000
        if limit > max_results:
            iterations = math.ceil(limit / max_results)
            df = pd.DataFrame()
            for i in range(0, iterations):
                print(
                    f"Getting transactions {i*max_results} through {(i+1)*max_results-1}."
                )
                offset = i * max_results
                transactions = asyncio.run(
                    mm.get_transactions(limit=1000, offset=offset)
                )
                df_temp = pd.json_normalize(transactions["allTransactions"]["results"])
                df = pd.concat([df, df_temp])
                df.reset_index(drop=True)
        else:
            transactions = asyncio.run(mm.get_transactions(limit=1000, offset=offset))
            df = pd.json_normalize(transactions["allTransactions"]["results"])
        df.columns = df.columns.str.replace(".", "_")
        return df


class TransactionTags(object):
    def get_transaction_tags(mm):
        tags = asyncio.run(mm.get_transaction_tags())
        df = pd.json_normalize(tags["householdTransactionTags"])
        df.columns = df.columns.str.replace(".", "_")
        return df
