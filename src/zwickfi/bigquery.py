"""BigQuery operations for loading data."""

import pandas as pd
from google.cloud import bigquery


def write_to_bigquery(
    df: pd.DataFrame,
    schema: str,
    table_name: str,
    client: bigquery.Client,
    project: str = "zwickfi",
) -> None:
    """
    Write a DataFrame to a BigQuery table, replacing existing data.

    Args:
        df: DataFrame to write.
        schema: BigQuery dataset/schema name.
        table_name: Target table name.
        client: Authenticated BigQuery client.
        project: GCP project ID.
    """
    table_id = f"{project}.{schema}.{table_name}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")
