from google.cloud import bigquery
import os
from pathlib import Path


class BigQuery(object):
    def write_to_bigquery(df, tablename):
        # try:
        #     root = Path(__file__).parent.parent.parent.parent
        #     relative_path = f'{root}/secrets/service-account-credentials.json'
        #     absolute_path = os.path.abspath(relative_path)
        #     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = absolute_path
        # except:
        #     pass
        """Load dataframe data into a specified BigQuery table."""
        table_id = f"zwickfi.monarch_money.{tablename}"
        client = bigquery.Client()
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        table = client.get_table(table_id)
        print(
            f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}"
        )
