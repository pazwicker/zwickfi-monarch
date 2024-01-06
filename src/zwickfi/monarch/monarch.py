import pandas as pd
import asyncio


class transaction_categories(object):
    def get_transaction_categories(mm):
        categories = asyncio.run(mm.get_transaction_categories())
        df = pd.json_normalize(categories["categories"])
        df.columns = df.columns.str.replace(".", "_")
        return df


class transactions(object):
    def get_transactions(mm):
        transactions = asyncio.run(mm.get_transactions())
        df = pd.json_normalize(transactions["allTransactions"]["results"])
        df.columns = df.columns.str.replace(".", "_")
        return df

class transaction_tags(object):
    def get_transaction_tags(mm):
        tags = asyncio.run(mm.get_transaction_tags())
        df = pd.json_normalize(tags["householdTransactionTags"])
        df.columns = df.columns.str.replace(".", "_")
        return df
