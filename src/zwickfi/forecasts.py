"""Credit card spending forecasts using Prophet."""

import pandas as pd
from google.cloud import bigquery
from prophet import Prophet


def get_forecast_data(client: bigquery.Client) -> tuple[pd.DataFrame, list[str]]:
    """
    Retrieve historical credit card spending data from BigQuery.

    Args:
        client: Authenticated BigQuery client.

    Returns:
        Tuple of (DataFrame with spending data, list of credit card names).
    """
    query = "SELECT * FROM analytics.credit_card_spending_for_forecast"
    query_job = client.query(query)
    results = query_job.result().to_dataframe()
    credit_cards = results["account_name"].unique().tolist()
    return results, credit_cards


def generate_forecasts(df: pd.DataFrame, credit_cards: list[str]) -> pd.DataFrame:
    """
    Generate 24-month spending forecasts for each credit card.

    Args:
        df: DataFrame with historical spending data.
        credit_cards: List of credit card account names.

    Returns:
        DataFrame with forecasted values for all credit cards.
    """
    df = df.copy()
    df["ds"] = df["due_month"]
    df["y"] = df["amount"]

    forecasts = []
    for credit_card in credit_cards:
        df_card = df.loc[df["account_name"] == credit_card, ["ds", "y"]].copy()

        model = Prophet()
        model.fit(df_card)

        future = model.make_future_dataframe(periods=24, freq="MS")
        forecast = model.predict(future)
        forecast["account_name"] = credit_card
        forecasts.append(forecast)

    result = pd.concat(forecasts, ignore_index=True)
    return result
