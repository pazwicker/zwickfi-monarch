"""Shared utility functions."""

import pandas as pd


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize a DataFrame by replacing dots with underscores in column names.

    Args:
        df: DataFrame to normalize.

    Returns:
        DataFrame with normalized column names.
    """
    if not df.empty:
        df.columns = df.columns.str.replace(".", "_", regex=False)
    return df


def json_to_dataframe(data: dict | list, key: str | None = None) -> pd.DataFrame:
    """
    Convert JSON data to a normalized DataFrame.

    Args:
        data: JSON data (dict or list).
        key: Optional key to extract from dict before normalizing.

    Returns:
        Normalized DataFrame.
    """
    if key is not None:
        data = data[key]
    df = pd.json_normalize(data)
    return normalize_dataframe(df)
