import pandas as pd
import asyncio


class zwickfi_transactions(object):
    def get_transactions(mm):
        transactions = asyncio.run(mm.get_transactions())
        df = pd.json_normalize(transactions["allTransactions"]["results"])
        df.columns = df.columns.str.replace(".", "_")
        return df
