# Claude Code Instructions

## Before Starting Work

**IMPORTANT**: Before beginning work on any PR, always:

1. Check out from main and pull the latest changes:
   ```bash
   git checkout main
   git pull origin main
   ```

2. Create a new branch for your work:
   ```bash
   git checkout -b <branch-name>
   ```

## Project Overview

This project syncs financial data from Monarch Money to Google BigQuery for analysis and forecasting.

## Project Structure

```
src/zwickfi/
├── __init__.py      # Package version
├── __main__.py      # Entry point for `python -m zwickfi`
├── cli.py           # Main orchestration logic
├── auth.py          # Authentication (Monarch Money + Google Cloud)
├── monarch.py       # Monarch Money API wrapper functions
├── bigquery.py      # BigQuery write operations
├── forecasts.py     # Prophet-based credit card forecasting
└── utils.py         # Shared utilities (DataFrame normalization)

tests/
├── conftest.py      # Pytest fixtures
└── test_monarch_api.py  # Integration tests for API methods
```

## Local Development Setup

1. Create and activate virtual environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install ruff pytest pytest-asyncio
   ```

3. Set environment variables (create `.env` file or export):
   ```bash
   export MONARCH_EMAIL="your-email"
   export MONARCH_PASSWORD="your-password"
   export MONARCH_SECRET_KEY="your-mfa-secret"
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"
   ```

4. Set PYTHONPATH for local development:
   ```bash
   export PYTHONPATH="$PWD/src"
   ```

## Running the Application

```bash
# As a module (recommended)
python -m zwickfi

# Or directly
python src/zwickfi/cli.py
```

## Running Tests

```bash
pytest tests/ -v
```

## Before Pushing Changes

**IMPORTANT**: Before pushing any changes to remote, test that modified files work correctly by pulling data from the Monarch API:

1. **Run the integration tests** to verify API connectivity and response structures:
   ```bash
   pytest tests/test_monarch_api.py -v
   ```

2. **If you modified `monarch.py` or `auth.py`**, manually test the affected functions:
   ```bash
   export PYTHONPATH="$PWD/src"
   python3 -c "
   from zwickfi.auth import get_monarch_client
   from zwickfi import monarch

   mm = get_monarch_client()

   # Test whichever functions you modified:
   print('Testing get_total_transactions...')
   count = monarch.get_total_transactions(mm)
   print(f'Total transactions: {count}')

   print('Testing get_transactions (limit=5)...')
   df = monarch.get_transactions(mm, limit=5)
   print(df.head())

   print('Testing get_accounts...')
   accounts = monarch.get_accounts(mm)
   print(accounts.head())

   print('Testing get_transaction_categories...')
   categories = monarch.get_transaction_categories(mm)
   print(categories.head())
   "
   ```

3. **If you modified `utils.py`**, verify DataFrame normalization works:
   ```bash
   python3 -c "
   from zwickfi.utils import json_to_dataframe, normalize_dataframe
   import pandas as pd

   # Test with sample nested data
   data = {'items': [{'foo.bar': 1, 'baz.qux': 2}]}
   df = json_to_dataframe(data, key='items')
   assert 'foo_bar' in df.columns
   print('utils.py tests passed')
   "
   ```

4. **Run linting** to ensure code quality:
   ```bash
   ruff check src/ tests/
   ruff format --check src/ tests/
   ```

**Note**: These tests hit the live Monarch Money API but do NOT write to BigQuery. Ensure your `MONARCH_*` environment variables are set.

## Code Formatting

This project uses `ruff` for linting and formatting:

```bash
# Check formatting
ruff format --check src/ tests/

# Auto-format
ruff format src/ tests/

# Lint
ruff check src/ tests/

# Lint and auto-fix
ruff check --fix src/ tests/
```

## Key Dependencies

- `monarchmoneycommunity`: Python client for Monarch Money API (supports new api.monarch.com endpoint)
- `pandas`: Data manipulation
- `google-cloud-bigquery`: BigQuery integration
- `prophet`: Time series forecasting

## Module Overview

### `auth.py`
- `get_monarch_client()` - Authenticate with Monarch Money
- `get_bigquery_client()` - Authenticate with Google Cloud

### `monarch.py`
- `get_total_transactions(mm)` - Get transaction count
- `get_transactions(mm, limit)` - Fetch transactions with pagination
- `get_transaction_categories(mm)` - Get categories
- `get_transaction_tags(mm)` - Get tags
- `get_accounts(mm)` - Get all accounts
- `get_account_history(mm, account_id)` - Get account balance history
- `get_budgets(mm, start_date, end_date)` - Get budget data

### `bigquery.py`
- `write_to_bigquery(df, schema, table_name, client)` - Load DataFrame to BigQuery

### `forecasts.py`
- `get_forecast_data(client)` - Query historical spending from BigQuery
- `generate_forecasts(df, credit_cards)` - Generate Prophet forecasts

### `utils.py`
- `normalize_dataframe(df)` - Replace dots with underscores in columns
- `json_to_dataframe(data, key)` - Convert JSON to normalized DataFrame

## CI/CD

GitHub Actions workflows:
- `test.yml` - Runs integration tests against Monarch Money API
- `lint.yml` - Checks code formatting with ruff
- `cloud-run-job.yml` - Builds and deploys to Google Cloud Run
