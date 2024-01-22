from prophet import Prophet
import pandas as pd
from google.cloud import bigquery
from datetime import date

# Get today's date
today = date.today().strftime("%Y-%m-%d")


class Forecasts(object):
    def get_forecast_data():
        client = bigquery.Client()
        query = "select * from analytics.credit_card_spending_for_forecast"
        query_job = client.query(query)
        results = query_job.result().to_dataframe()
        credit_cards = results["account_name"].unique()
        return results, credit_cards

    def get_forecasts(df, credit_cards):
        df["ds"] = df["due_month"]
        df["y"] = df["amount"]
        forecast = pd.DataFrame()
        for credit_card in credit_cards:
            df_filtered = df.loc[(df["account_name"] == credit_card)]
            df_fcst = df_filtered[["ds", "y"]].copy()
            m = Prophet()
            m.fit(df_fcst)
            future = m.make_future_dataframe(periods=24, freq="MS")
            forecast_temp = m.predict(future)
            forecast_temp["account_name"] = credit_card
            forecast = pd.concat([forecast, forecast_temp])
        forecast.reset_index(drop=True, inplace=True)
        return forecast
