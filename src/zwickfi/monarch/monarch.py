import pandas as pd
import asyncio
from typing import Optional
import math


class Transactions(object):
    def get_total_transactions(mm):
        """
        Retrieves the total number of transactions from the Monarch Money service.

        Args:
            mm (MonarchMoney): An authenticated MonarchMoney object.

        Returns:
            int: The total number of transactions.
        """
        transactions_summary = asyncio.run(mm.get_transactions_summary())
        total_transactions = pd.json_normalize(
            transactions_summary["aggregates"][0]["summary"]
        )["count"].iloc[0]
        return total_transactions

    def get_transactions(mm, limit: Optional[int] = 1000):
        """
        Retrieves transactions from the Monarch Money service up to the specified limit.

        Args:
            mm (MonarchMoney): An authenticated MonarchMoney object.
            limit (int, optional): The maximum number of transactions to retrieve. Defaults to 1000.

        Returns:
            pandas.DataFrame: A DataFrame containing transaction data.
        """
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

    def get_transaction_categories(mm):
        """
        Retrieves transaction categories from the Monarch Money service.

        Args:
            mm (MonarchMoney): An authenticated MonarchMoney object.

        Returns:
            pandas.DataFrame: A DataFrame containing transaction category data.
        """
        categories = asyncio.run(mm.get_transaction_categories())
        df = pd.json_normalize(categories["categories"])
        df.columns = df.columns.str.replace(".", "_")
        return df

    def get_transaction_tags(mm):
        """
        Retrieves transaction tags from the Monarch Money service.

        Args:
            mm (MonarchMoney): An authenticated MonarchMoney object.

        Returns:
            pandas.DataFrame: A DataFrame containing transaction tag data.
        """
        tags = asyncio.run(mm.get_transaction_tags())
        df = pd.json_normalize(tags["householdTransactionTags"])
        df.columns = df.columns.str.replace(".", "_")
        return df


class Accounts(object):
    def get_accounts(mm):
        accounts = asyncio.run(mm.get_accounts)
        df = pd.json_normalize(accounts["accounts"])
        df.columns = df.columns.str.replace(".", "_")
        return df

    def get_account_history(mm, account_id):
        account_history = asyncio.run(mm.get_account_history(account_id))
        df = pd.json_normalize(account_history)
        df.columns = df.columns.str.replace(".", "_")
        return df
