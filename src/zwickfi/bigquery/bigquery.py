from google.cloud import bigquery


class BigQuery(object):
    def write_to_bigquery(df, tablename):
        """
        Writes the given DataFrame to a BigQuery table, truncating the existing table.

        This method takes a pandas DataFrame and writes it to a specified BigQuery table.
        If the table already exists, its contents are replaced with the new data (WRITE_TRUNCATE).

        Args:
            df (pandas.DataFrame): The DataFrame to write to BigQuery.
            tablename (str): The name of the BigQuery table where the data will be written. The
                             table name should be specified in a 'dataset.table' format.

        Prints:
            The number of rows and columns loaded into the BigQuery table.

        Note:
            The method assumes that the BigQuery client is authorized and the dataset
            'zwickfi.monarch_money' already exists in your BigQuery project.
        """
        table_id = f"zwickfi.monarch_money.{tablename}"
        client = bigquery.Client()
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Waits for the job to complete
        table = client.get_table(table_id)  # Retrieves the table to confirm the upload
        print(
            f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}"
        )
