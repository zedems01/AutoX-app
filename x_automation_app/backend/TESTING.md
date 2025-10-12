# Backend Testing Guide

Guide to testing the X Automation backend application.

## Quick Start

### 1. Install Dependencies

```bash
cd x_automation_app/backend
uv add httpx pytest pytest-asyncio pytest-cov pytest-mock python-dotenv"
```

### 2. Run Tests

```bash
# On Unix/Linux/macOS
./run_tests.sh

# Or directly with pytest
pytest
```

### 3. View Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open report (Unix/macOS)
open htmlcov/index.html
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test Categories

```bash
# API tests only
pytest tests/test_api/

# Utility tests only
pytest tests/test_utils/

# State tests only
pytest tests/test_state/

# Graph tests only
pytest tests/test_graph/

# Integration tests only
pytest tests/test_integration/
```

### Run Specific Test Files
```bash
pytest tests/test_api/test_auth.py
pytest tests/test_utils/test_x_utils.py
```

### Run Specific Test Classes
```bash
pytest tests/test_api/test_auth.py::TestLogin
pytest tests/test_utils/test_x_utils.py::TestGetCharCount
```

### Run Specific Tests
```bash
pytest tests/test_api/test_auth.py::TestLogin::test_login_with_valid_credentials
```

### Run Tests by Marker
```bash
# Skip integration tests
pytest -m "not integration"

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow
```

## Test Options

### Coverage Reports
```bash
# Terminal report
pytest --cov=app

# HTML report
pytest --cov=app --cov-report=html

# XML report (for CI)
pytest --cov=app --cov-report=xml

# Multiple formats
pytest --cov=app --cov-report=html --cov-report=term
```

### Output Control
```bash
# Verbose output
pytest -v

# Very verbose (show test names and output)
pytest -vv

# Quiet mode (minimal output)
pytest -q

# Show print statements
pytest -s
```

### Debugging
```bash
# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Enter debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l
```

### Performance
```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Show slowest tests
pytest --durations=10
```

## Using Test Scripts

```bash
chmod +x run_tests.sh

# Run all tests
./run_tests.sh

# Run with coverage
./run_tests.sh coverage

# Run specific category
./run_tests.sh api
./run_tests.sh utils
./run_tests.sh state
./run_tests.sh graph
./run_tests.sh integration

# Run fast tests (skip integration)
./run_tests.sh fast
```
