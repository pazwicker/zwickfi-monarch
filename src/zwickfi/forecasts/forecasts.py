from prophet import Prophet
import pandas as pd
from datetime import date


# Get today's date
today = date.today().strftime("%Y-%m-%d")


class Forecasts:
    def __init__(self, bigquery_client):
        """
        Initialize the Forecasts class with an authenticated BigQuery client.

        Args:
            bigquery_client (bigquery.Client): Authenticated BigQuery client.
        """
        self.client = bigquery_client

    def get_forecast_data(self):
        """
        Retrieve forecast data from BigQuery.

        Returns:
            tuple: A DataFrame of results and a list of unique credit card names.
        """
        query = "SELECT * FROM analytics.credit_card_spending_for_forecast"
        query_job = self.client.query(query)
        results = query_job.result().to_dataframe()
        credit_cards = results["account_name"].unique()
        return results, credit_cards

    @staticmethod
    def get_forecasts(df, credit_cards):
        """
        Generate forecasts for each credit card using Prophet.

        Args:
            df (pd.DataFrame): DataFrame containing forecast data.
            credit_cards (list): List of unique credit card names.

        Returns:
            pd.DataFrame: DataFrame with forecasted values.
        """
        df["ds"] = df["due_month"]
        df["y"] = df["amount"]
        forecast = pd.DataFrame()
        for credit_card in credit_cards:
            df_filtered = df.loc[df["account_name"] == credit_card]
            df_fcst = df_filtered[["ds", "y"]].copy()
            m = Prophet()
            m.fit(df_fcst)
            future = m.make_future_dataframe(periods=24, freq="MS")
            forecast_temp = m.predict(future)
            forecast_temp["account_name"] = credit_card
            forecast = pd.concat([forecast, forecast_temp])
        forecast.reset_index(drop=True, inplace=True)
        return forecast
