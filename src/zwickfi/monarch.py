"""Monarch Money API wrapper for extracting financial data."""

import asyncio
import math
from datetime import datetime

import pandas as pd
from monarchmoney import MonarchMoney

from .utils import json_to_dataframe


def get_total_transactions(mm: MonarchMoney) -> int:
    """
    Get the total number of transactions.

    Args:
        mm: Authenticated MonarchMoney client.

    Returns:
        Total transaction count.
    """
    summary = asyncio.run(mm.get_transactions_summary())
    total = summary["aggregates"][0]["summary"]["count"]
    print(f"Total transactions: {total}")
    return total


def get_transactions(mm: MonarchMoney, limit: int = 1000) -> pd.DataFrame:
    """
    Retrieve transactions with pagination support.

    Args:
        mm: Authenticated MonarchMoney client.
        limit: Maximum number of transactions to retrieve.

    Returns:
        DataFrame containing transaction data.
    """
    max_per_request = 1000
    df = pd.DataFrame()

    if limit > max_per_request:
        iterations = math.ceil(limit / max_per_request)
        for i in range(iterations):
            offset = i * max_per_request
            print(
                f"Getting transactions {offset} through {offset + max_per_request - 1}."
            )
            transactions = asyncio.run(
                mm.get_transactions(limit=max_per_request, offset=offset)
            )
            df_temp = json_to_dataframe(transactions, key=None)
            # Handle nested structure
            df_temp = json_to_dataframe(transactions["allTransactions"]["results"])
            df = pd.concat([df, df_temp], ignore_index=True)
    else:
        transactions = asyncio.run(mm.get_transactions(limit=limit, offset=0))
        df = json_to_dataframe(transactions["allTransactions"]["results"])

    return df


def get_transaction_categories(mm: MonarchMoney) -> pd.DataFrame:
    """
    Retrieve transaction categories.

    Args:
        mm: Authenticated MonarchMoney client.

    Returns:
        DataFrame containing category data.
    """
    categories = asyncio.run(mm.get_transaction_categories())
    return json_to_dataframe(categories, key="categories")


def get_transaction_tags(mm: MonarchMoney) -> pd.DataFrame:
    """
    Retrieve transaction tags.

    Args:
        mm: Authenticated MonarchMoney client.

    Returns:
        DataFrame containing tag data.
    """
    tags = asyncio.run(mm.get_transaction_tags())
    return json_to_dataframe(tags, key="householdTransactionTags")


def get_accounts(mm: MonarchMoney) -> pd.DataFrame:
    """
    Retrieve all accounts.

    Args:
        mm: Authenticated MonarchMoney client.

    Returns:
        DataFrame containing account data.
    """
    accounts = asyncio.run(mm.get_accounts())
    return json_to_dataframe(accounts, key="accounts")


def get_account_history(mm: MonarchMoney, account_id: str) -> pd.DataFrame:
    """
    Retrieve balance history for a specific account.

    Args:
        mm: Authenticated MonarchMoney client.
        account_id: Account ID to get history for.

    Returns:
        DataFrame containing account history.
    """
    history = asyncio.run(mm.get_account_history(account_id))
    return json_to_dataframe(history)


def get_budgets(
    mm: MonarchMoney,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """
    Retrieve budget data.

    Args:
        mm: Authenticated MonarchMoney client.
        start_date: Start date in "yyyy-mm-dd" format.
        end_date: End date in "yyyy-mm-dd" format.

    Returns:
        DataFrame containing budget data with synced_at timestamp.
    """
    synced_at = datetime.now()
    budgets = asyncio.run(mm.get_budgets(start_date=start_date, end_date=end_date))
    df = json_to_dataframe(budgets)
    df["synced_at"] = synced_at
    return df
