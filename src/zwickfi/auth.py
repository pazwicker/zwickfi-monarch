"""Authentication utilities for Monarch Money and Google Cloud."""

import asyncio
import os

from google.cloud import bigquery
from google.oauth2 import service_account
from monarchmoney import MonarchMoney


def get_monarch_client() -> MonarchMoney:
    """
    Create and authenticate a Monarch Money client.

    Credentials are read from environment variables:
    - MONARCH_EMAIL
    - MONARCH_PASSWORD
    - MONARCH_SECRET_KEY

    If environment variables are not set, prompts for input.

    Returns:
        Authenticated MonarchMoney client.

    Raises:
        Exception: If login fails.
    """
    mm = MonarchMoney(timeout=60)

    monarch_email = os.getenv("MONARCH_EMAIL")
    monarch_password = os.getenv("MONARCH_PASSWORD")
    monarch_secret_key = os.getenv("MONARCH_SECRET_KEY")

    if not monarch_email:
        monarch_email = _prompt_required("MONARCH_EMAIL", "Monarch Money email")

    if not monarch_password:
        monarch_password = _prompt_required(
            "MONARCH_PASSWORD", "Monarch Money password"
        )

    if not monarch_secret_key:
        monarch_secret_key = _prompt_required(
            "MONARCH_SECRET_KEY", "Monarch Money secret key"
        )

    try:
        asyncio.run(
            mm.login(
                email=monarch_email,
                password=monarch_password,
                save_session=False,
                use_saved_session=False,
                mfa_secret_key=monarch_secret_key,
            )
        )
        print("Successfully logged in to Monarch Money.")
    except Exception as e:
        print(f"Failed to log in to Monarch Money: {e}")
        raise

    return mm


def get_bigquery_client() -> bigquery.Client:
    """
    Create and authenticate a BigQuery client.

    Credentials are read from the GOOGLE_APPLICATION_CREDENTIALS environment variable.
    If not set, prompts for the service account file path.

    Returns:
        Authenticated BigQuery client.

    Raises:
        FileNotFoundError: If service account file doesn't exist.
    """
    service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not service_account_file:
        service_account_file = input(
            "The environment variable 'GOOGLE_APPLICATION_CREDENTIALS' is not set.\n"
            "Please provide the full path to your service_account.json file: "
        )
        if not os.path.exists(service_account_file):
            raise FileNotFoundError(
                f"Service account file not found: {service_account_file}"
            )
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_file

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file
    )
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    print("Authenticated with Google Cloud.")
    return client


def _prompt_required(env_var: str, description: str) -> str:
    """Prompt for a required value that wasn't set in environment."""
    value = input(
        f"The environment variable '{env_var}' is not set.\n"
        f"Please enter your {description}: "
    ).strip()
    while not value:
        value = input(f"{description} cannot be empty. Please enter again: ").strip()
    return value
