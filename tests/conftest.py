"""Pytest configuration and fixtures."""

import asyncio
import os
import sys

import pytest
from monarchmoney import MonarchMoney

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def monarch_client(event_loop):
    """
    Create and authenticate a MonarchMoney client for testing.

    Requires environment variables:
    - MONARCH_EMAIL
    - MONARCH_PASSWORD
    - MONARCH_SECRET_KEY
    """
    mm = MonarchMoney(timeout=60)

    email = os.getenv("MONARCH_EMAIL")
    password = os.getenv("MONARCH_PASSWORD")
    secret_key = os.getenv("MONARCH_SECRET_KEY")

    if not all([email, password, secret_key]):
        pytest.skip("Monarch Money credentials not configured")

    event_loop.run_until_complete(
        mm.login(
            email=email,
            password=password,
            save_session=False,
            use_saved_session=False,
            mfa_secret_key=secret_key,
        )
    )

    return mm
