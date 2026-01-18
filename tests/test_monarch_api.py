"""
Integration tests for Monarch Money API methods.

These tests verify that:
1. The monarchmoneycommunity package can authenticate successfully
2. Each API method returns data in the expected format
3. The response structures match what our code expects

Tests pull minimal data to avoid long runtimes.
"""

import pandas as pd
import pytest


class TestAuthentication:
    """Test that authentication works with the new api.monarch.com endpoint."""

    def test_login_succeeds(self, monarch_client):
        """Verify that we can authenticate with Monarch Money."""
        assert monarch_client is not None


class TestTransactionsMethods:
    """Test transaction-related API methods."""

    def test_get_transactions_summary(self, monarch_client, event_loop):
        """Test get_transactions_summary returns expected structure with count."""
        summary = event_loop.run_until_complete(
            monarch_client.get_transactions_summary()
        )

        assert "aggregates" in summary
        assert "summary" in summary["aggregates"]
        assert "count" in summary["aggregates"]["summary"]
        assert isinstance(summary["aggregates"]["summary"]["count"], int)

    def test_get_transactions(self, monarch_client, event_loop):
        """Test get_transactions returns expected structure."""
        transactions = event_loop.run_until_complete(
            monarch_client.get_transactions(limit=5)
        )

        assert "allTransactions" in transactions
        assert "results" in transactions["allTransactions"]
        assert isinstance(transactions["allTransactions"]["results"], list)

        if transactions["allTransactions"]["results"]:
            df = pd.json_normalize(transactions["allTransactions"]["results"])
            assert isinstance(df, pd.DataFrame)

    def test_get_transaction_categories(self, monarch_client, event_loop):
        """Test get_transaction_categories returns expected structure."""
        categories = event_loop.run_until_complete(
            monarch_client.get_transaction_categories()
        )

        assert "categories" in categories
        assert isinstance(categories["categories"], list)

        df = pd.json_normalize(categories["categories"])
        assert isinstance(df, pd.DataFrame)

    def test_get_transaction_tags(self, monarch_client, event_loop):
        """Test get_transaction_tags returns expected structure."""
        tags = event_loop.run_until_complete(monarch_client.get_transaction_tags())

        assert "householdTransactionTags" in tags
        assert isinstance(tags["householdTransactionTags"], list)

        df = pd.json_normalize(tags["householdTransactionTags"])
        assert isinstance(df, pd.DataFrame)


class TestAccountsMethods:
    """Test account-related API methods."""

    def test_get_accounts(self, monarch_client, event_loop):
        """Test get_accounts returns expected structure."""
        accounts = event_loop.run_until_complete(monarch_client.get_accounts())

        assert "accounts" in accounts
        assert isinstance(accounts["accounts"], list)

        df = pd.json_normalize(accounts["accounts"])
        assert isinstance(df, pd.DataFrame)

    def test_get_account_history(self, monarch_client, event_loop):
        """Test get_account_history returns data for a valid account."""
        accounts = event_loop.run_until_complete(monarch_client.get_accounts())

        if not accounts["accounts"]:
            pytest.skip("No accounts available for testing")

        account_id = accounts["accounts"][0]["id"]

        history = event_loop.run_until_complete(
            monarch_client.get_account_history(account_id)
        )

        df = pd.json_normalize(history)
        assert isinstance(df, pd.DataFrame)


class TestBudgetsMethods:
    """Test budget-related API methods."""

    def test_get_budgets(self, monarch_client, event_loop):
        """Test get_budgets returns expected structure."""
        budgets = event_loop.run_until_complete(
            monarch_client.get_budgets(start_date="2024-01-01", end_date="2024-01-31")
        )

        df = pd.json_normalize(budgets)
        assert isinstance(df, pd.DataFrame)
