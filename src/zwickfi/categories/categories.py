import pandas as pd
import asyncio


class zwickfi_transaction_categories(object):
    def get_transaction_categories(mm):
        transactions = asyncio.run(mm.get_transaction_categories())
        df = pd.json_normalize(transactions["categories"])
        df.columns = df.columns.str.replace(".", "_")
        return df
