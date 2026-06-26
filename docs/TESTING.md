# Testing Guide

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html

# Specific file
pytest tests/test_database.py -v
```

## Test Structure

| File | Type | Coverage |
|------|------|----------|
| `test_auth_utils.py` | Unit | Password hashing, validation |
| `test_text_metrics.py` | Unit | Token estimation, readability |
| `test_gemini_service.py` | Unit/API | Gemini service with mocks |
| `test_database.py` | Database | Auth + prompt CRUD |
| `test_integration.py` | Integration | Cross-service workflows |
| `test_startup.py` | Startup | Import verification, DB init |

## Test Isolation

- Each test uses a temporary SQLite database via `conftest.py`
- Environment variables mocked for consistent test runs
- Gemini API calls mocked — no real API key needed for tests

## Writing New Tests

```python
def test_my_feature():
    with get_services() as services:
        user = services.auth.register(UserCreate(...))
        # assert expected behavior
```

## CI Integration

```yaml
# Example GitHub Actions
- run: pip install -r requirements.txt
- run: pytest tests/ -v
```

## Expected Results

All 23 tests should pass:
- 4 auth utility tests
- 4 database tests
- 4 Gemini service tests
- 4 integration tests
- 2 startup tests
- 5 text metrics tests
