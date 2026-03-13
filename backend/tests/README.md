# Backend Tests

This directory contains comprehensive tests for the backend application.

## Test Structure

The test structure mirrors the application structure for better organization:

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Shared fixtures and configuration
├── test_models.py                 # Pydantic model validation tests
├── test_cloudflare_client.py      # Cloudflare API client tests
├── api/                           # API layer tests
│   ├── __init__.py
│   ├── test_routes.py             # API endpoint tests
│   └── test_exception_handlers.py # Exception handler tests
├── services/                      # Service layer tests
│   ├── __init__.py
│   └── test_crawl_service.py      # Crawl service business logic tests
├── .coveragerc                    # Coverage configuration
├── README.md                      # This file
├── QUICKSTART.md                  # Quick start guide
└── TESTING_SUMMARY.md             # Implementation summary
```

This structure matches the `app/` directory organization:
- `tests/api/` → `app/api/`
- `tests/services/` → `app/services/`
- `tests/test_*.py` → `app/*.py`

## Setup

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Environment Variables

Create a `.env` file in the backend directory (or use `.env.example` as template):

```bash
CLOUDFLARE_ACCOUNT_ID=test_account_id
CLOUDFLARE_API_TOKEN=test_token
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
PORT=8000
LOG_LEVEL=INFO
```

## Running Tests

### Local Development

#### Run All Tests

```bash
cd backend
pytest
```

#### Run with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

This generates:
- Terminal coverage report
- HTML coverage report in `tests/reports/coverage/` directory
- XML coverage report in `tests/reports/coverage.xml`
- JUnit XML report in `tests/reports/junit/results.xml`

### Docker Container (Recommended)

Running tests in a Docker container ensures consistency across environments and saves test artifacts to a mounted directory for easy access.

#### Run Tests in Container

```bash
# From project root
docker-compose --profile test run --rm backend-test
```

This will:
- Build the backend container if needed
- Run all tests with coverage
- Save reports to `backend/tests/reports/` (accessible on your host machine)
- Clean up the container after completion

#### View Test Reports

After running tests in the container, reports are available locally:

```bash
# Open HTML coverage report
open backend/tests/reports/coverage/index.html

# View JUnit XML results
cat backend/tests/reports/junit/results.xml

# View coverage XML
cat backend/tests/reports/coverage.xml
```

#### Benefits of Container Testing

1. **Environment Consistency**: Tests run in the same environment as production
2. **Isolation**: No conflicts with local Python versions or dependencies
3. **Accessibility**: All test artifacts saved locally for review
4. **Reproducibility**: Same results across different developer machines
5. **CI/CD Ready**: Same setup can be used in continuous integration

#### Clean Up Test Reports

```bash
# Remove all test reports
rm -rf backend/tests/reports/coverage backend/tests/reports/junit/results.xml backend/tests/reports/coverage.xml
```

Note: The `reports/` directory is in `.gitignore` and won't be committed to version control.

### Run Specific Test Files

```bash
# Test models only
pytest tests/test_models.py

# Test API routes only
pytest tests/api/test_routes.py

# Test exception handlers only
pytest tests/api/test_exception_handlers.py

# Test crawl service only
pytest tests/services/test_crawl_service.py

# Test Cloudflare client only
pytest tests/test_cloudflare_client.py

# Test all API layer tests
pytest tests/api/

# Test all service layer tests
pytest tests/services/
```

### Run Specific Test Classes or Methods

```bash
# Run specific test class
pytest tests/test_models.py::TestCrawlRequest

# Run specific test method
pytest tests/test_models.py::TestCrawlRequest::test_valid_request

# Run specific API test
pytest tests/api/test_routes.py::TestHealthEndpoint::test_health_check

# Run specific service test
pytest tests/services/test_crawl_service.py::TestCrawlService::test_initiate_crawl_success
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests and Stop on First Failure

```bash
pytest -x
```

### Run Tests in Parallel

```bash
pytest -n auto
```

## Test Categories

### 1. Model Tests (`test_models.py`)

**Location**: `tests/test_models.py`

Tests Pydantic model validation:
- Valid input acceptance
- Invalid input rejection
- Default values
- Field constraints (min/max, patterns)
- URL validation
- Enum validation

**Example:**
```python
def test_valid_request(self):
    """Test valid crawl request."""
    request = CrawlRequest(url="https://example.com", depth=2)
    assert str(request.url) == "https://example.com/"
    assert request.depth == 2
```

### 2. Cloudflare Client Tests (`test_cloudflare_client.py`)

**Location**: `tests/test_cloudflare_client.py`

Tests Cloudflare API integration:
- Successful API calls
- Error handling (401, 429, 500, 502)
- Network errors
- Response parsing
- Result transformation

**Uses `respx` for HTTP mocking:**
```python
async def test_initiate_crawl_success(self, client, mock_settings):
    with respx.mock:
        route = respx.post(f"{mock_settings.cloudflare_api_base_url}/crawl")
            .mock(return_value=httpx.Response(200, json=response_data))
        
        result = await client.initiate_crawl("https://example.com", 2)
        assert result["job_id"] == "test-job-id-123"
```

### 3. Crawl Service Tests (`services/test_crawl_service.py`)

**Location**: `tests/services/test_crawl_service.py`

Tests business logic layer:
- Crawl initiation
- Status retrieval
- Error propagation
- Service initialization

**Uses `unittest.mock` for mocking:**
```python
async def test_initiate_crawl_success(self, service, mock_cloudflare_client):
    mock_cloudflare_client.initiate_crawl.return_value = {
        "job_id": "test-job-123",
        "status": "running"
    }
    service.cloudflare_client = mock_cloudflare_client
    
    result = await service.initiate_crawl(request)
    assert result.job_id == "test-job-123"
```

### 4. API Route Tests (`api/test_routes.py`)

**Location**: `tests/api/test_routes.py`

Tests FastAPI endpoints:
- Health check endpoint
- Crawl initiation endpoint
- Job status endpoint
- Request validation
- Error responses
- CORS headers

**Uses FastAPI TestClient:**
```python
def test_health_check(self, client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 5. Exception Handler Tests (`api/test_exception_handlers.py`)

**Location**: `tests/api/test_exception_handlers.py`

Tests custom exception handlers:
- Cloudflare API error mapping
- Validation error handling
- Global exception handling
- Status code mapping
- Error response format

**Tests handler functions directly:**
```python
async def test_handler_401_error(self, mock_request):
    error = CloudflareAPIError("Invalid credentials", status_code=401)
    response = await cloudflare_api_error_handler(mock_request, error)
    assert response.status_code == 401
```

## Fixtures

### Shared Fixtures (`conftest.py`)

- `mock_settings`: Mock application settings
- `app`: FastAPI application instance
- `client`: Synchronous test client
- `async_client`: Asynchronous test client
- `sample_crawl_request`: Sample crawl request data
- `sample_cloudflare_initiate_response`: Mock Cloudflare initiation response
- `sample_cloudflare_status_response`: Mock Cloudflare status response
- `sample_cloudflare_running_response`: Mock running job response
- `sample_cloudflare_error_response`: Mock error response

## Mocking Strategies

### HTTP Requests (respx)

For testing Cloudflare API client:

```python
import respx
import httpx

with respx.mock:
    respx.post("https://api.cloudflare.com/...").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    # Test code here
```

### Async Functions (AsyncMock)

For testing services:

```python
from unittest.mock import AsyncMock

mock_client = MagicMock()
mock_client.initiate_crawl = AsyncMock(return_value={"job_id": "123"})
```

### Patching

For testing routes:

```python
from unittest.mock import patch

with patch("app.api.routes.crawl_service") as mock_service:
    mock_service.initiate_crawl = AsyncMock(return_value=response)
    # Test code here
```

## Coverage Goals

Target coverage: **>90%**

Current coverage areas:
- ✅ Models: 100%
- ✅ Cloudflare Client: ~95%
- ✅ Crawl Service: ~95%
- ✅ API Routes: ~90%
- ✅ Exception Handlers: ~90%

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Create .env file
        run: |
          echo "CLOUDFLARE_ACCOUNT_ID=test_account" >> backend/.env
          echo "CLOUDFLARE_API_TOKEN=test_token" >> backend/.env
          echo "CORS_ORIGINS=http://localhost:3000" >> backend/.env
      
      - name: Run tests in Docker
        run: docker-compose --profile test run --rm backend-test
      
      - name: Upload coverage reports
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: backend/tests/reports/
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: backend/tests/reports/coverage.xml
          fail_ci_if_error: true
```

### Alternative: Local Python Setup

```yaml
name: Tests (Local Python)

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml:tests/reports/coverage.xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          files: backend/tests/reports/coverage.xml
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Use descriptive test names that explain what is being tested
3. **Arrange-Act-Assert**: Follow AAA pattern in tests
4. **Mock External Dependencies**: Don't make real API calls
5. **Test Edge Cases**: Include boundary conditions and error cases
6. **Keep Tests Fast**: Use mocks to avoid slow operations
7. **Maintain Fixtures**: Keep shared fixtures in `conftest.py`
8. **Document Complex Tests**: Add docstrings explaining test purpose

## Troubleshooting

### Import Errors

If you see import errors:
```bash
# Ensure you're in the backend directory
cd backend

# Install in development mode
pip install -e .
```

### Async Test Errors

If async tests fail:
```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```

### Coverage Not Working

```bash
# Reinstall coverage tools
pip install --upgrade pytest-cov coverage
```

### Mock Not Working

```bash
# Ensure you're patching the right import path
# Patch where the object is used, not where it's defined
```

## Adding New Tests

When adding new functionality:

1. **Write tests first** (TDD approach)
2. **Add fixtures** to `conftest.py` if reusable
3. **Follow existing patterns** in similar test files
4. **Update this README** if adding new test categories
5. **Ensure coverage** doesn't drop below 90%

### Example: Adding a New Endpoint Test

```python
# In test_routes.py

class TestNewEndpoint:
    """Tests for new endpoint."""
    
    def test_new_endpoint_success(self, client):
        """Test successful request to new endpoint."""
        response = client.get("/api/new-endpoint")
        
        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data
    
    def test_new_endpoint_error(self, client):
        """Test error handling in new endpoint."""
        response = client.get("/api/new-endpoint?invalid=param")
        
        assert response.status_code == 400
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [respx Documentation](https://lundberg.github.io/respx/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

## Contact

For questions about tests, refer to:
- [`AGENTS.md`](../AGENTS.md) - Developer guidance
- [`ARCHITECTURE.md`](../ARCHITECTURE.md) - System architecture
- [`README.md`](../README.md) - Project overview